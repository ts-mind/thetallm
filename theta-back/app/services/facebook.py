import logging
import requests
from app.core.config import settings

logger = logging.getLogger("theta.facebook")


class FacebookService:
    def __init__(self):
        self.base_url = settings.FB_GRAPH_URL
        self.page_token = settings.FB_PAGE_ACCESS_TOKEN

    def _get(self, endpoint: str, params: dict = None) -> dict:
        url = f"{self.base_url}/{endpoint}"
        if params is None: params = {}
        params["access_token"] = self.page_token
        try:
            r = requests.get(url, params=params, timeout=10)
            return r.json()
        except requests.RequestException as e:
            logger.error(f"Graph GET /{endpoint} failed: {e}")
            return {"error": {"message": str(e)}}

    def _post(self, endpoint: str, payload: dict) -> dict:
        url = f"{self.base_url}/{endpoint}"
        payload["access_token"] = self.page_token
        try:
            r = requests.post(url, json=payload, timeout=10)
            return r.json()
        except requests.RequestException as e:
            logger.error(f"Graph POST /{endpoint} failed: {e}")
            return {}

    # ── GENERIC TOOLS ──

    def get_object(self, object_id: str, fields: str = None) -> dict:
        """Generic fetcher to get specific fields (like 'from') of any object."""
        params = {"fields": fields} if fields else {}
        return self._get(object_id, params=params)

    def get_user_profile(self, psid: str) -> dict:
        """Fetch basic public info (Name) of a user who messaged the page."""
        data = self._get(psid, fields="name,first_name")
        if "error" in data:
            return {"name": "User", "first_name": "Friend"}
        return data

    # ── CONTEXT FETCHERS (The Missing Methods) ──

    def get_post_context(self, post_id: str) -> str:
        """Fetches the text content of a post to give the AI context."""
        data = self._get(post_id, params={"fields": "message,caption,description"})

        if "error" in data:
            logger.error(f"❌ Failed to fetch post {post_id}: {data['error'].get('message')}")
            return ""

        # Return the most relevant text field found
        text = data.get("message") or data.get("description") or data.get("caption") or ""
        return text

    def get_comment_context(self, comment_id: str, post_id: str) -> str:
        """Fetches the comment AND the original post to understand the full context."""
        # 1. Fetch the comment
        c_data = self._get(comment_id, params={"fields": "message"})
        comment_text = c_data.get("message", "")

        # 2. Fetch the parent post
        p_data = self._get(post_id, params={"fields": "message,description"})
        post_text = p_data.get("message") or p_data.get("description") or "Image/Video Post"

        return f"Post Content: \"{post_text}\"\nUser Comment: \"{comment_text}\""

    # ── ACTIONS ──

    def post_comment(self, object_id: str, message: str) -> dict:
        return self._post(f"{object_id}/comments", {"message": message})

    def post_message(self, recipient_id: str, text: str) -> dict:
        return self._post("me/messages", {
            "recipient": {"id": recipient_id},
            "messaging_type": "RESPONSE",
            "message": {"text": text},
        })


fb_service = FacebookService()