import logging
import requests
import re
from app.core.config import settings

logger = logging.getLogger("theta.facebook")


class FacebookService:
    def __init__(self):
        self.base_url = settings.FB_GRAPH_URL
        self.page_token = settings.FB_PAGE_ACCESS_TOKEN

        # Headers: We impersonate a standard Desktop Browser for the Embed endpoint
        self.headers_desktop = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        # Headers: We impersonate an Old Android Phone for mBasic
        self.headers_mobile = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-A205U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Mobile Safari/537.36",
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

    # ── THE "TRIPLE TAP" SCRAPER ──

    def _scrape_post_fallback(self, full_post_id: str) -> str:
        """
        Tries 3 different URL structures to find the post content.
        """
        try:
            # Parse ID: "PageID_PostID" -> user_id, post_id
            parts = full_post_id.split("_")
            if len(parts) != 2:
                logger.error(f"❌ Invalid ID format for scraping: {full_post_id}")
                return ""

            user_id, post_id = parts

            # 🎯 STRATEGY 1: The Embed Endpoint (Most Reliable for Public Posts)
            # Facebook puts the post content inside the embed HTML for 3rd party sites.
            embed_url = f"https://www.facebook.com/plugins/post.php?href=https%3A%2F%2Fwww.facebook.com%2F{user_id}%2Fposts%2F{post_id}&width=500"
            logger.info(f"⛏️ Trying Embed: {embed_url}")

            resp = requests.get(embed_url, headers=self.headers_desktop, timeout=5)
            if resp.status_code == 200:
                text = self._extract_text(resp.text)
                if text: return text

            # 🎯 STRATEGY 2: mBasic Corrected Path
            # Path: /UserID/posts/PostID
            mbasic_url = f"https://mbasic.facebook.com/{user_id}/posts/{post_id}"
            logger.info(f"⛏️ Trying mBasic Path: {mbasic_url}")

            resp = requests.get(mbasic_url, headers=self.headers_mobile, timeout=5)
            if resp.status_code == 200:
                text = self._extract_text(resp.text)
                if text: return text

            # 🎯 STRATEGY 3: Legacy Story Path
            # Path: /story.php?story_fbid=PostID&id=UserID
            story_url = f"https://mbasic.facebook.com/story.php?story_fbid={post_id}&id={user_id}"
            logger.info(f"⛏️ Trying Story Path: {story_url}")

            resp = requests.get(story_url, headers=self.headers_mobile, timeout=5)
            if resp.status_code == 200:
                text = self._extract_text(resp.text)
                if text: return text

            return ""

        except Exception as e:
            logger.error(f"❌ Scraping error: {e}")
            return ""

    def _extract_text(self, html: str) -> str:
        """Helper to pull text from HTML soup using Regex."""
        # 1. Try Meta Description (Cleanest)
        match = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', html, re.IGNORECASE)
        if match:
            text = match.group(1)
            if "Log into Facebook" not in text and "Facebook" != text:
                return text

        # 2. Try Title
        match_title = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
        if match_title:
            text = match_title.group(1)
            if "Log into" not in text and "Facebook" != text:
                return text

        return ""

    def get_post_context(self, post_id: str) -> str:
        """Fetches post text via API, falls back to Scraping."""
        # 1. Try API
        data = self._get(post_id, params={"fields": "message,caption,description"})
        if "error" not in data:
            return data.get("message") or data.get("description") or data.get("caption") or ""

        # 2. API Failed? ENABLE SCRAPE MODE
        logger.warning(f"⚠️ API blocked reading {post_id}. Engaging Scraper...")
        scraped_text = self._scrape_post_fallback(post_id)

        if scraped_text:
            logger.info(f"✅ Scrape Successful: {scraped_text[:30]}...")
            return scraped_text

        return ""

    def get_comment_context(self, comment_id: str, post_id: str) -> str:
        # 1. Fetch the comment
        c_data = self._get(comment_id, params={"fields": "message"})
        comment_text = c_data.get("message", "")

        # 2. Fetch the parent post
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