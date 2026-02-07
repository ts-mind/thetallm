import logging
import requests
import re
from app.core.config import settings

logger = logging.getLogger("theta.facebook")


class FacebookService:
    def __init__(self):
        self.base_url = settings.FB_GRAPH_URL
        self.page_token = settings.FB_PAGE_ACCESS_TOKEN

        # 🛠️ UPDATED: Mobile User-Agent for mbasic access
        self.scrape_headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-A205U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Mobile Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://mbasic.facebook.com/",
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

    # ── THE "MBASIC" SCRAPER ──

    def _scrape_post_fallback(self, post_id: str) -> str:
        """
        Fallback: Scrapes mbasic.facebook.com (Static HTML) when API fails.
        """
        try:
            # 1. Clean ID: Convert "PageID_PostID" -> "PostID"
            clean_id = post_id.split("_")[-1]

            # 2. Target mbasic (The "Dumb Phone" version)
            # This version has NO React, NO complex blocking scripts.
            target_url = f"https://mbasic.facebook.com/{clean_id}"

            logger.info(f"⛏️ Scraping mbasic: {target_url}")

            # 3. Request
            resp = requests.get(target_url, headers=self.scrape_headers, timeout=5)

            if resp.status_code != 200:
                logger.warning(f"Scrape failed with code {resp.status_code}")
                return ""

            html = resp.text

            # 4. Extraction Strategy

            # Strategy A: Meta Description (Best for "Summary")
            match = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', html, re.IGNORECASE)
            if match:
                text = match.group(1)
                # Cleanup "Log into Facebook" trash
                if "Log into Facebook" not in text:
                    return text

            # Strategy B: Title Tag (mbasic often puts the post content in title)
            match_title = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
            if match_title:
                text = match_title.group(1)
                # If title is just "Facebook" or "Log In", it failed.
                if "Facebook" not in text and "Log In" not in text:
                    return text

            # Strategy C: Raw Body Text (Desperation Move)
            # In mbasic, the main post is often in a <p> or <div>.
            # This is hard to regex cleanly without BS4, but let's try a simple grab.
            # (Skipping for now to avoid garbage data)

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
        logger.warning(f"⚠️ API blocked reading {post_id}. Engaging mBasic Scraper...")
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