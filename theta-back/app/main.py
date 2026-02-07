import json
import logging
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.services.brain import brain
from app.services.facebook import fb_service
from app.services.db import init_db, increment_posts_analyzed, increment_dms_answered, get_stats

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("theta")

init_db()
app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ... (Keep health/stats/verify endpoints) ...
@app.get("/webhook")
async def verify(request: Request):
    p = request.query_params
    if p.get("hub.mode") == "subscribe" and p.get("hub.verify_token") == settings.FB_VERIFY_TOKEN:
        return int(p.get("hub.challenge"))
    return "Failed", 403

# ── WEBHOOK ROUTER ──
@app.post("/webhook")
async def webhook(request: Request, bg: BackgroundTasks):
    data = await request.json()
    if data.get("object") != "page": return {"status": "ignored"}

    for entry in data.get("entry", []):
        # 1. MESSAGES (DM)
        for msg in entry.get("messaging", []):
            sender = msg.get("sender", {}).get("id")
            text = msg.get("message", {}).get("text")
            if sender == settings.PAGE_ID: continue
            if text:
                logger.info(f"📩 DM from {sender}: {text}")
                bg.add_task(process_dm, sender, text)

        # 2. FEED / MENTIONS
        for change in entry.get("changes", []):
            field = change.get("field")
            val = change.get("value", {})
            if field == "feed":
                _handle_feed(val, bg)
            elif field in ("mentions", "mention"):
                _handle_mention(val, bg)

    return {"status": "received"}

# ── HANDLERS ──

def _handle_feed(val: dict, bg: BackgroundTasks):
    item = val.get("item")
    verb = val.get("verb")
    sender_id = str(val.get("from", {}).get("id", ""))
    if sender_id == settings.PAGE_ID: return
    if item == "comment" and verb == "add":
        bg.add_task(process_comment, val.get("post_id"), val.get("comment_id"), sender_id)

def _handle_mention(val: dict, bg: BackgroundTasks):
    if val.get("verb") != "add": return
    post_id = val.get("post_id", "")
    comment_id = val.get("comment_id")
    target_id = comment_id if comment_id else post_id
    sender_id = str(val.get("sender_id", ""))
    if sender_id == settings.PAGE_ID: return

    if post_id and target_id:
        logger.info(f"🏷️ BOT SUMMONED (Target: {target_id})")
        bg.add_task(process_mention, post_id, target_id, sender_id)

# ── WORKERS ──

async def process_dm(sender_id: str, text: str):
    if not text or not text.strip(): return
    logger.info(f"⚡ Processing DM for {sender_id}")
    reply = brain.chat_reply(text)
    fb_service.post_message(sender_id, reply)
    increment_dms_answered()
    logger.info("✅ DM answered")

async def process_mention(post_id: str, target_id: str, user_psid: str):
    logger.info(f"⚡ Processing mention on {target_id}")

    # 1. GHOST USER FIX
    if not user_psid:
        try:
            obj = fb_service.get_object(target_id, fields="from")
            if obj and "from" in obj:
                user_psid = obj["from"]["id"]
                logger.info(f"🔍 Resolved Sender ID: {user_psid}")
        except Exception:
            pass

    # 2. Get Context (The Post Content)
    context = fb_service.get_post_context(post_id)
    if not context: return

    # 3. 🌟 DECISION: Chat vs Verify?
    # If the user says "verify", "check", or "fact", we use the new Research Tool.
    content_lower = context.lower()
    if any(k in content_lower for k in ["verify", "fact check", "check this", "সত্যতা", "যাচাই"]):
        logger.info("🕵️ Verification Intent Detected")
        reply_text = brain.verify_post(context)
    else:
        # Standard witty reply
        reply_text = brain.analyze_and_reply(context)

    # 4. Reply
    final_reply = f"@[{user_psid}] {reply_text}" if user_psid else reply_text
    fb_service.post_comment(target_id, final_reply)
    increment_posts_analyzed()
    logger.info("✅ Mention answered")

async def process_comment(post_id: str, comment_id: str, user_psid: str):
    context = fb_service.get_comment_context(comment_id, post_id)
    if not context: return
    reply = brain.analyze_and_reply(context)
    fb_service.post_comment(comment_id, f"@[{user_psid}] {reply}")
    increment_posts_analyzed()