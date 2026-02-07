import logging
import requests
from app.core.config import settings

logger = logging.getLogger("theta.facebook")


class FacebookService:
    # ... (Keep your existing _get and _post methods) ...

    def _get(self, endpoint: str, params: dict = None) -> dict:
        url = f"{settings.FB_GRAPH_URL}/{endpoint}"
        if params is None: params = {}
        params["access_token"] = settings.FB_PAGE_ACCESS_TOKEN
        try:
            r = requests.get(url, params=params, timeout=10)
            return r.json()
        except requests.RequestException as e:
            logger.error(f"Graph GET /{endpoint} failed: {e}")
            return {"error": {"message": str(e)}}

    def _post(self, endpoint: str, payload: dict) -> dict:
        url = f"{settings.FB_GRAPH_URL}/{endpoint}"
        payload["access_token"] = settings.FB_PAGE_ACCESS_TOKEN
        try:
            r = requests.post(url, json=payload, timeout=10)
            return r.json()
        except requests.RequestException as e:
            logger.error(f"Graph POST /{endpoint} failed: {e}")
            return {}

    # 🌟 NEW METHOD: Generic Object Fetcher
    def get_object(self, object_id: str, fields: str = None) -> dict:
        """Generic fetcher to get specific fields (like 'from') of any object."""
        params = {"fields": fields} if fields else {}
        return self._get(object_id, params=params)

    # ... (Keep post_comment, post_message, get_post_context, etc.) ...

    def post_comment(self, object_id: str, message: str) -> dict:
        return self._post(f"{object_id}/comments", {"message": message})

    def post_message(self, recipient_id: str, text: str) -> dict:
        return self._post("me/messages", {
            "recipient": {"id": recipient_id},
            "messaging_type": "RESPONSE",
            "message": {"text": text},
        })

    # (Include your existing context fetching methods here: get_post_context, etc.)
    # I am omitting them for brevity, but DO NOT DELETE THEM from your file.


fb_service = FacebookService()