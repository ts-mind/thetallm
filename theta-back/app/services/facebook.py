import logging
import requests
import re
import json
import html
from app.core.config import settings

logger = logging.getLogger("theta.facebook")


class FacebookService:
    def __init__(self):
        self.base_url = settings.FB_GRAPH_URL
        self.page_token = settings.FB_PAGE_ACCESS_TOKEN

        # 🎭 HEADERS: Masquerade as a Desktop Browser (Crucial for Embeds)
        self.headers_desktop = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Sec-Fetch-Dest": "iframe",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
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
            data = r.json()

            # 🚨 NEW: Catch the Privacy Error
            if "error" in data:
                logger.error(f"❌ FB POST ERROR: {data['error'].get('message')} (Code: {data['error'].get('code')})")

            return data
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

    # ── THE "EMBED" SCRAPER (Success Strategy) ──

    def _scrape_post_fallback(self, full_post_id: str) -> str:
        """
        Scrapes the public 'Embed' endpoint to get text and images.
        Returns a JSON string: '{"text": "...", "images": [...]}'
        """
        try:
            parts = full_post_id.split("_")
            if len(parts) != 2: return ""
            user_id, post_id = parts

            # 🎯 URL: The Public Embed Plugin
            embed_url = f"https://www.facebook.com/plugins/post.php?href=https%3A%2F%2Fwww.facebook.com%2F{user_id}%2Fposts%2F{post_id}&width=500"
            logger.info(f"⛏️ Scraping Embed: {embed_url}")

            resp = requests.get(embed_url, headers=self.headers_desktop, timeout=8)
            if resp.status_code != 200:
                logger.warning(f"Scrape failed: {resp.status_code}")
                return ""

            # 🕵️ EXTRACTION
            content = resp.text
            data = {"text": "", "images": []}

            # 1. TEXT: Extract from <p> tags
            p_matches = re.findall(r'<p[^>]*>(.*?)</p>', content, re.DOTALL)
            valid_lines = []
            for p in p_matches:
                clean = self._clean_html(p)
                if len(clean) > 2 and "Facebook" not in clean:
                    valid_lines.append(clean)

            if valid_lines:
                data["text"] = "\n".join(valid_lines)
            else:
                # Fallback: Meta Description
                meta_match = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', content, re.IGNORECASE)
                if meta_match:
                    data["text"] = self._clean_html(meta_match.group(1))

            # 2. IMAGES: Extract & Filter
            img_matches = re.findall(r'<img[^>]+src="([^"]+)"', content)
            for img_url in img_matches:
                img_url = html.unescape(img_url)

                # 🛡️ FILTER: Remove Profile Pics (s50x50, cp0_dst) & Icons
                if any(x in img_url for x in ["s50x50", "p50x50", "cp0_dst", "static", "emoji"]):
                    continue

                # Must be a content image (usually served from scontent)
                if "scontent" in img_url and img_url not in data["images"]:
                    data["images"].append(img_url)

            # 3. FINALIZE: Nullify images if empty
            if not data["images"]:
                data["images"] = None

            # Return JSON string so Brain can read it structurally
            return json.dumps(data, ensure_ascii=False)

        except Exception as e:
            logger.error(f"❌ Scraping error: {e}")
            return ""

    def _clean_html(self, raw_html: str) -> str:
        """Removes tags and unescapes entities."""
        if not raw_html: return ""
        text = html.unescape(raw_html)
        text = re.sub(r'<[^>]+>', '', text)
        return text.strip()

    def get_post_context(self, post_id: str) -> str:
        """Fetches post text via API, falls back to Scraping."""
        # 1. Try API (Returns plain text)
        data = self._get(post_id, params={"fields": "message,caption,description"})
        if "error" not in data:
            return data.get("message") or data.get("description") or data.get("caption") or ""

        # 2. API Failed? ENABLE SCRAPE MODE (Returns JSON String)
        logger.warning(f"⚠️ API blocked reading {post_id}. Engaging Scraper...")
        scraped_json = self._scrape_post_fallback(post_id)

        if scraped_json:
            logger.info(f"✅ Scrape Successful")
            return scraped_json

        return ""

    def get_comment_context(self, comment_id: str, post_id: str) -> str:
        # 1. Fetch the comment
        c_data = self._get(comment_id, params={"fields": "message"})
        comment_text = c_data.get("message", "")

        # 2. Fetch the parent post
        post_context = self.get_post_context(post_id)
        if not post_context: post_context = "[Post Content Hidden]"

        return f"Post Context: {post_context}\nUser Comment: \"{comment_text}\""

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