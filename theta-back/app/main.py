# backend/app/main.py
import json
import logging
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.services.brain import brain
from app.services.facebook import fb_service
from app.services.db import init_db, increment_posts_analyzed, get_stats

# Setup logging so we can see what's happening
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("theta")

# Initialize DB on startup
init_db()

app = FastAPI(title=settings.PROJECT_NAME)

origins = [
    "http://localhost:3000",
    "https://theta.tservice.tech",
]

# CORS for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROUTES ---

@app.get("/")
def home():
    return {"status": "Theta LLM Backend Online", "version": settings.VERSION}

@app.get("/stats")
def stats_endpoint():
    count = get_stats()
    return {
        "posts_analyzed": count,
        "model": "Theta-Gemini-Flash-2.0",
        "status": "OPERATIONAL"
    }

@app.get("/debug")
def debug_endpoint():
    """Debug endpoint — shows config state (no secrets). Remove in production."""
    return {
        "page_id_configured": bool(settings.PAGE_ID),
        "page_id_value": settings.PAGE_ID[:6] + "..." if settings.PAGE_ID else "NOT SET",
        "fb_token_configured": bool(settings.FB_PAGE_ACCESS_TOKEN),
        "fb_token_length": len(settings.FB_PAGE_ACCESS_TOKEN),
        "verify_token_configured": bool(settings.FB_VERIFY_TOKEN),
        "google_key_configured": bool(settings.GOOGLE_API_KEY),
        "environment": settings.ENVIRONMENT,
        "webhook_url": "https://api.tservice.tech/webhook",
        "cors_origins": origins,
    }

# Facebook Verification (The Handshake)
@app.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")
    
    logger.info(f"🤝 Webhook verification: mode={mode}, token_match={token == settings.FB_VERIFY_TOKEN}")
    
    if mode == "subscribe" and token == settings.FB_VERIFY_TOKEN:
        logger.info(f"✅ Webhook verified! Returning challenge: {challenge}")
        return int(challenge)
    
    logger.warning(f"❌ Webhook verification FAILED. Expected token: {settings.FB_VERIFY_TOKEN[:10]}...")
    return "Verification Failed", 403

# The Event Listener
@app.post("/webhook")
async def handle_webhook(request: Request, tasks: BackgroundTasks):
    body = await request.body()
    data = await request.json()
    
    # === CRITICAL DEBUG LOG ===
    # Log the FULL raw payload so we can see exactly what Facebook sends
    logger.info(f"📨 WEBHOOK POST received. Raw payload:\n{json.dumps(data, indent=2)}")
    
    try:
        # Facebook sends: { "object": "page", "entry": [...] }
        obj = data.get("object")
        logger.info(f"📌 Object type: {obj}")
        
        if obj != "page":
            logger.warning(f"⚠️ Unexpected object type: {obj}. Expected 'page'.")
            return {"status": "ignored_non_page"}
        
        for entry in data.get("entry", []):
            page_id = entry.get("id")
            time = entry.get("time")
            logger.info(f"📄 Entry from page: {page_id}, time: {time}")
            
            # Handle messaging events (Messenger)
            messaging = entry.get("messaging", [])
            for msg_event in messaging:
                sender_id = msg_event.get("sender", {}).get("id", "")
                logger.info(f"💬 Messaging event from sender: {sender_id}")
                # Future: handle Messenger messages here
            
            # Handle changes (feed, mentions)
            for change in entry.get("changes", []):
                field = change.get("field")
                val = change.get("value", {})
                logger.info(f"🔔 Change field: '{field}', value keys: {list(val.keys())}")
                
                if field == "feed":
                    item = val.get("item")
                    verb = val.get("verb")
                    sender_id = str(val.get("sender_id", val.get("from", {}).get("id", "")))
                    
                    logger.info(f"📝 Feed event: item={item}, verb={verb}, sender={sender_id}")
                    
                    # Avoid self-reply loops
                    if sender_id == settings.PAGE_ID:
                        logger.info(f"🔄 Skipping self-generated event from our page")
                        continue
                    
                    # Handle comment events
                    if item == "comment" and verb in ("add", "edited"):
                        comment_id = val.get("comment_id")
                        post_id = val.get("post_id")
                        logger.info(f"💬 Comment detected: comment={comment_id}, post={post_id}")
                        
                        if comment_id and post_id:
                            tasks.add_task(process_mention, post_id, comment_id)
                            logger.info(f"✅ Task queued for processing")
                    
                    # Handle post events (status, photo, video, etc.)
                    elif item == "status" and verb == "add":
                        post_id = val.get("post_id")
                        logger.info(f"📝 New post detected: {post_id}")
                
                elif field == "mentions":
                    post_id = val.get("post_id", "")
                    target_id = val.get("comment_id", post_id)
                    sender_id = str(val.get("sender_id", ""))
                    
                    logger.info(f"🏷️ Mention event: post={post_id}, target={target_id}, sender={sender_id}")
                    
                    if sender_id != settings.PAGE_ID:
                        tasks.add_task(process_mention, post_id, target_id)
                        logger.info(f"✅ Mention task queued")
                
                else:
                    logger.info(f"ℹ️ Unhandled field: '{field}' — logging for debug")
                
    except Exception as e:
        # We must return 200 OK or FB will disable the webhook
        logger.error(f"🔥 Webhook Parse Error: {e}", exc_info=True)
        
    return {"status": "received"}

# The Worker Process
async def process_mention(post_id: str, target_id: str):
    logger.info(f"⚡ Processing mention for post: {post_id}, replying to: {target_id}")
    
    # 1. Get Full Context (walk up the tree)
    context = fb_service.get_post_context(post_id)
    if not context:
        logger.warning(f"⚠️ No context found for post: {post_id}")
        return
    
    logger.info(f"📖 Context fetched ({len(context)} chars): {context[:200]}...")

    # 2. Analyze with The Brain
    reply = brain.analyze_and_reply(context)
    logger.info(f"🧠 Brain reply ({len(reply)} chars): {reply[:200]}...")
    
    # 3. Reply to the comment/post
    fb_service.post_comment(target_id, reply)
    
    # 4. Update Stats
    increment_posts_analyzed()
    logger.info(f"✅ Mention processed successfully")
