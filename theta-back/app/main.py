import json
import logging

from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.services.brain import brain
from app.services.facebook import fb_service
from app.services.db import init_db, increment_posts_analyzed, increment_dms_answered, get_stats

# ── Logging ──
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("theta")

# ── App ──
init_db()
app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://theta.tservice.tech"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ====================================================================
#  Health / Stats / Debug
# ====================================================================

@app.get("/")
def health():
    return {"status": "Theta AI Backend Online", "version": settings.VERSION}


@app.get("/stats")
def stats():
    counts = get_stats()
    return {
        "comments_analyzed": counts.get("posts_analyzed", 0),
        "dms_answered": counts.get("dms_answered", 0),
        "model": "gemini-2.0-flash",
        "status": "OPERATIONAL",
    }


@app.get("/debug")
def debug():
    return {
        "page_id": settings.PAGE_ID[:8] + "…" if settings.PAGE_ID else "NOT SET",
        "fb_token_len": len(settings.FB_PAGE_ACCESS_TOKEN),
        "verify_token_set": bool(settings.FB_VERIFY_TOKEN),
        "gemini_key_set": bool(settings.GOOGLE_API_KEY),
        "env": settings.ENVIRONMENT,
    }


# ====================================================================
#  Webhook — Verification (GET)
# ====================================================================

@app.get("/webhook")
async def verify(request: Request):
    p = request.query_params
    mode, token, challenge = p.get("hub.mode"), p.get("hub.verify_token"), p.get("hub.challenge")

    if mode == "subscribe" and token == settings.FB_VERIFY_TOKEN:
        logger.info(f"Webhook verified (challenge={challenge})")
        return int(challenge)

    logger.warning("Webhook verification failed")
    return {"error": "verification_failed"}, 403


# ====================================================================
#  Webhook — Event Router (POST)
# ====================================================================

@app.post("/webhook")
async def webhook(request: Request, bg: BackgroundTasks):
    data = await request.json()
    logger.info(f"📨 Incoming webhook:\n{json.dumps(data, indent=2)}")

    if data.get("object") != "page":
        return {"status": "ignored"}

    for entry in data.get("entry", []):

        # ────────────────────────────────────────────
        #  Lane 1 — Private Messages (Messenger DMs)
        # ────────────────────────────────────────────
        for msg_event in entry.get("messaging", []):
            sender_id = msg_event.get("sender", {}).get("id", "")
            text = msg_event.get("message", {}).get("text", "")

            if sender_id == settings.PAGE_ID:
                continue                                       # skip echo of our own replies

            if not text:
                logger.info(f"📩 DM from {sender_id}: (non-text — attachment/reaction, skipped)")
                continue

            logger.info(f"📩 DM from {sender_id}: {text}")
            bg.add_task(process_dm, sender_id, text)

        # ────────────────────────────────────────────
        #  Lane 2 — Public Feed (comments / mentions)
        # ────────────────────────────────────────────
        for change in entry.get("changes", []):
            field = change.get("field")
            val = change.get("value", {})

            if field == "feed":
                _handle_feed(val, bg)

            elif field == "mention":
                _handle_mention(val, bg)

            else:
                logger.info(f"Unhandled field: {field}")

    return {"status": "received"}


# ── Feed sub-router ──

def _handle_feed(val: dict, bg: BackgroundTasks):
    item = val.get("item")
    verb = val.get("verb")
    sender = val.get("from", {})
    sender_id = str(sender.get("id", ""))
    sender_name = sender.get("name", "Unknown")
    message = val.get("message", "")

    if sender_id == settings.PAGE_ID:
        logger.info("🔄 Self-event (our own page), skipping")
        return

    if item == "comment" and verb in ("add", "edited"):
        comment_id = val.get("comment_id", "")
        post_id = val.get("post_id", "")
        logger.info(f"💬 Comment from {sender_name}: {message}")
        logger.info(f"   comment_id={comment_id}  post_id={post_id}  user_id={sender_id}")

        if comment_id and post_id:
            bg.add_task(process_comment, post_id, comment_id, sender_id)

    elif item == "status" and verb == "add":
        logger.info(f"📝 New post by {sender_name} (post_id={val.get('post_id')})")

    else:
        logger.info(f"Feed event: item={item} verb={verb} (no action)")


def _handle_mention(val: dict, bg: BackgroundTasks):
    item = val.get("item")           # "comment", "post", "status", …
    verb = val.get("verb")           # "add", "edited", "remove"

    if verb != "add":
        logger.info(f"Mention verb={verb}, ignoring (only act on 'add')")
        return

    post_id = val.get("post_id", "")
    comment_id = val.get("comment_id")       # None when tagged in the post caption itself
    sender_id = str(val.get("sender_id", ""))
    sender_name = val.get("sender_name", "Someone")

    if sender_id == settings.PAGE_ID:
        return

    # If tagged in a comment → reply to that comment.
    # If tagged in a post caption → reply to the post.
    target_id = comment_id if comment_id else post_id

    logger.info(f"🏷️ BOT SUMMONED by {sender_name} in {item}")
    logger.info(f"   post_id={post_id}  comment_id={comment_id}  sender={sender_id}  target={target_id}")

    if post_id and target_id:
        bg.add_task(process_mention, post_id, target_id, sender_id)


# ====================================================================
#  Workers
# ====================================================================

async def process_dm(sender_id: str, text: str):
    """Lane 1 worker — answer a Messenger DM."""
    logger.info(f"⚡ Processing DM for: {sender_id}")

    reply = brain.chat_reply(text)
    logger.info(f"🧠 Reply: {reply[:200]}")

    fb_service.post_message(sender_id, reply)
    increment_dms_answered()
    logger.info("✅ DM answered")


async def process_comment(post_id: str, comment_id: str, user_psid: str):
    """Lane 2a — someone commented on our page's post."""
    logger.info(f"⚡ Processing comment on {post_id} from {user_psid}")

    context = fb_service.get_comment_context(comment_id, post_id)
    if not context:
        logger.warning(f"No context for post={post_id}, comment={comment_id}")
        return

    logger.info(f"📖 Context ({len(context)} chars): {context[:300]}")

    reply_text = brain.analyze_and_reply(context)
    reply_with_tag = f"@[{user_psid}] {reply_text}"
    logger.info(f"🧠 Reply: {reply_with_tag[:200]}")

    fb_service.post_comment(comment_id, reply_with_tag)
    increment_posts_analyzed()
    logger.info("✅ Comment answered")


async def process_mention(post_id: str, target_id: str, user_psid: str):
    """Lane 2b — someone @tagged the bot on an external post/comment."""
    logger.info(f"⚡ Processing mention on {post_id} from {user_psid}")

    # Mention context: the post might be privacy-blocked.
    # get_post_context handles that and returns a fallback string.
    context = fb_service.get_post_context(post_id)
    logger.info(f"📖 Context ({len(context)} chars): {context[:300]}")

    reply_text = brain.analyze_and_reply(context)
    reply_with_tag = f"@[{user_psid}] {reply_text}"
    logger.info(f"🧠 Reply: {reply_with_tag[:200]}")

    fb_service.post_comment(target_id, reply_with_tag)
    increment_posts_analyzed()
    logger.info("✅ Mention answered")
