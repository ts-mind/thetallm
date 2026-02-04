# backend/app/services/facebook.py
import requests
from app.core.config import settings

class FacebookService:
    def get_post_content(self, post_id: str) -> str:
        """Fetches the text content of a specific post."""
        url = f"{settings.FB_GRAPH_URL}/{post_id}"
        params = {
            "fields": "message",
            "access_token": settings.FB_PAGE_ACCESS_TOKEN
        }
        resp = requests.get(url, params=params)
        data = resp.json()
        return data.get("message", "")

    def post_comment(self, object_id: str, message: str):
        """Replies to a post or comment."""
        url = f"{settings.FB_GRAPH_URL}/{object_id}/comments"
        params = {
            "message": message,
            "access_token": settings.FB_PAGE_ACCESS_TOKEN
        }
        try:
            r = requests.post(url, params=params)
            r.raise_for_status()
            print(f"✅ Replied to {object_id}")
        except Exception as e:
            print(f"❌ Failed to reply: {e}")

fb_service = FacebookService()