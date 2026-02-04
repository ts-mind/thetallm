# backend/app/main.py
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.services.brain import brain
from app.services.facebook import fb_service
from app.services.db import init_db, increment_posts_analyzed, get_stats

# Initialize DB on startup
init_db()

app = FastAPI(title=settings.PROJECT_NAME)

# CORS for Vercel Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Change to ["https://tservice.tech"] in production
    allow_methods=["GET"],
    allow_headers=["*"],
)

# --- ROUTES ---

@app.get("/")
def home():
    return {"status": "TeraMind Backend Online", "version": settings.VERSION}

@app.get("/stats")
def stats_endpoint():
    count = get_stats()
    return {
        "posts_analyzed": count,
        "model": "Theta-Gemini-Flash-2.0",
        "status": "OPERATIONAL"
    }

# Facebook Verification (The Handshake)
@app.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == settings.FB_VERIFY_TOKEN:
        return int(params.get("hub.challenge"))
    return "Verification Failed", 403

# The Event Listener
@app.post("/webhook")
async def handle_webhook(request: Request, tasks: BackgroundTasks):
    data = await request.json()
    
    try:
        entry = data['entry'][0]
        changes = entry['changes'][0]
        
        if changes['field'] == 'mentions':
            val = changes['value']
            post_id = val['post_id']
            # Reply to the comment if it's a comment, otherwise the post
            target_id = val.get('comment_id', post_id)
            sender_id = val['sender_id']
            
            # Avoid self-reply loops
            # You'll need to put your actual Page ID here eventually
            if sender_id != "YOUR_PAGE_ID": 
                tasks.add_task(process_mention, post_id, target_id)
                
    except Exception as e:
        # We must return 200 OK or FB will disable the webhook
        print(f"Webhook Parse Error: {e}")
        pass
        
    return {"status": "received"}

# The Worker Process
async def process_mention(post_id: str, target_id: str):
    print(f"⚡ Processing mention for {post_id}")
    
    # 1. Get Content
    text = fb_service.get_post_content(post_id)
    if not text:
        return

    # 2. Analyze
    reply = brain.analyze_and_reply(text)
    
    # 3. Reply
    fb_service.post_comment(target_id, reply)
    
    # 4. Update Stats
    increment_posts_analyzed()