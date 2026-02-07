import logging
import requests
import re
from app.core.config import settings

logger = logging.getLogger("theta.facebook")


class FacebookService:
    def __init__(self):
        self.base_url = settings.FB_GRAPH_URL
        self.page_token = settings.FB_PAGE_ACCESS_TOKEN
        # Headers to look like a real Chrome browser (bypasses basic scraping blocks)
        self.scrape_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }

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
        params = {"fields": fields} if fields else {}
        return self._get(object_id, params=params)

    def get_user_profile(self, psid: str) -> dict:
        data = self._get(psid, fields="name,first_name")
        if "error" in data:
            return {"name": "User", "first_name": "Friend"}
        return data

    # ── THE "PUSH THROUGH" LOGIC ──

    def _scrape_post_fallback(self, post_id: str) -> str:
        """
        When API fails, we scrape the public HTML metadata.
        """
        try:
            # 1. Clean ID: Convert "PageID_PostID" -> "PostID"
            clean_id = post_id.split("_")[-1]

            # 2. Construct Public URL
            # We try the mobile URL first (m.facebook.com) as it's lighter
            target_url = f"https://www.facebook.com/{clean_id}"

            logger.info(f"⛏️ Scraping fallback: {target_url}")

            # 3. Request (Impersonating Browser)
            resp = requests.get(target_url, headers=self.scrape_headers, timeout=5)

            if resp.status_code != 200:
                logger.warning(f"Scrape failed with code {resp.status_code}")
                return ""

            # 4. Extract Text using Regex (No heavy BS4 needed)
            # Facebook puts post text in <meta name="description" content="...">
            # or <title> ... </title>
            html = resp.text

            # Search for meta description
            match = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', html, re.IGNORECASE)
            if match:
                text = match.group(1)
                # Cleanup: remove "Log in..." generic text if caught
                if "Log into Facebook" in text: return ""
                return text

            # Search for Title as backup
            match_title = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
            if match_title:
                text = match_title.group(1)
                if "Facebook" not in text:  # If it's just "Facebook", it failed
                    return text

            return ""

        except Exception as e:
            logger.error(f"❌ Scraping error: {e}")
            return ""

    def get_post_context(self, post_id: str) -> str:
        """Fetches post text via API, falls back to Scraping."""
        # 1. Try API
        data = self._get(post_id, params={"fields": "message,caption,description"})

        if "error" not in data:
            return data.get("message") or data.get("description") or data.get("caption") or ""

        # 2. API Failed? ENABLE SCRAPE MODE
        logger.warning(f"⚠️ API blocked reading {post_id}. Engaging Scraping Fallback...")
        scraped_text = self._scrape_post_fallback(post_id)

        if scraped_text:
            logger.info(f"✅ Scrape Successful: {scraped_text[:30]}...")
            return scraped_text

        return ""

    def get_comment_context(self, comment_id: str, post_id: str) -> str:
        # 1. Fetch the comment
        c_data = self._get(comment_id, params={"fields": "message"})
        comment_text = c_data.get("message", "")

        # 2. Fetch the parent post (Using the new robust method)
        post_text = self.get_post_context(post_id)
        if not post_text: post_text = "[Post Content Hidden]"

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