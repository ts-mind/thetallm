import logging
import requests
from app.core.config import settings

logger = logging.getLogger("theta.facebook")


class FacebookService:
    """
    Two traffic lanes, one service:
      - Public Feed:  post_comment()   → POST /{object_id}/comments
      - Private DM:   post_message()   → POST /me/messages
      - Context:      get_post_context()  → walk the Graph API tree
    """

    # =================================================================
    #  Graph API transport
    # =================================================================

    def _get(self, endpoint: str, fields: str) -> dict:
        """
        GET from Graph API.  Does NOT raise on 4xx so callers can
        inspect the {"error": ...} body (e.g. privacy-blocked posts).
        """
        url = f"{settings.FB_GRAPH_URL}/{endpoint}"
        params = {"fields": fields, "access_token": settings.FB_PAGE_ACCESS_TOKEN}
        try:
            r = requests.get(url, params=params, timeout=10)
            data = r.json()
            if "error" in data:
                logger.warning(f"Graph GET /{endpoint} → error: {data['error'].get('message', 'unknown')}")
            return data
        except requests.RequestException as e:
            logger.error(f"Graph GET /{endpoint} network failure: {e}")
            return {"error": {"message": str(e), "type": "NetworkError"}}

    def _post(self, endpoint: str, payload: dict) -> dict:
        url = f"{settings.FB_GRAPH_URL}/{endpoint}"
        payload["access_token"] = settings.FB_PAGE_ACCESS_TOKEN
        try:
            r = requests.post(url, json=payload, timeout=15)
            r.raise_for_status()
            data = r.json()
            logger.info(f"Graph POST /{endpoint} → {data}")
            return data
        except requests.RequestException as e:
            logger.error(f"Graph POST /{endpoint} failed: {e}")
            return {}

    # =================================================================
    #  Lane 1 — Public Feed (comments)
    # =================================================================

    def post_comment(self, object_id: str, message: str) -> dict:
        """Reply publicly to a post or comment on the feed."""
        return self._post(f"{object_id}/comments", {"message": message})

    # =================================================================
    #  Lane 2 — Private DM (Messenger)
    # =================================================================

    def post_message(self, recipient_id: str, text: str) -> dict:
        """Send a private message via the Messenger Send API."""
        return self._post("me/messages", {
            "recipient": {"id": recipient_id},
            "messaging_type": "RESPONSE",
            "message": {"text": text},
        })

    # =================================================================
    #  Context Fetching — "Walk Up the Tree"
    # =================================================================

    def get_post_context(self, post_id: str) -> str:
        """
        Primary context entry point for mentions.

        Tries fetching as a post first.  If the Graph API returns an error
        (privacy block, expired token, etc.) returns a graceful fallback
        so the bot still replies instead of staying silent.
        Falls back to comment-walk if the ID isn't a post.
        """
        data = self._get(post_id, "message,caption,description,story,from,full_picture,attachments{description,media,subattachments}")

        # ── Graph API error (privacy block, permissions, etc.) ──
        if "error" in data:
            err_msg = data["error"].get("message", "Unknown error")
            logger.warning(f"Cannot read post {post_id}: {err_msg}")
            return (
                "I was tagged on a post, but I cannot read its content "
                "due to Facebook privacy settings or permissions. "
                "Try tagging me on a public post instead!"
            )

        # ── Empty response (deleted post, etc.) ──
        if not data or data.get("id") is None:
            return self._walk_comment(post_id)

        return self._format_post(data)

    def get_comment_context(self, comment_id: str, post_id: str) -> str:
        """
        Build a full picture: root post + the triggering comment.
        Used by the feed-comment worker so the LLM sees everything.
        """
        parts: list[str] = []

        # Root post
        post_data = self._get(post_id, "message,story,from,attachments{description,media,subattachments}")
        if post_data and "error" not in post_data:
            parts.append(self._format_post(post_data))

        # The comment itself (+ parent if it's a reply-to-reply)
        comment_ctx = self._walk_comment(comment_id)
        if comment_ctx:
            parts.append(comment_ctx)

        return "\n\n".join(parts)

    # ── internal helpers ──

    def _walk_comment(self, comment_id: str) -> str:
        """Fetch a comment and, if it has a parent, walk one level up."""
        data = self._get(comment_id, "message,from,created_time,parent,attachment")
        if not data or "error" in data:
            logger.warning(f"Could not fetch comment {comment_id}")
            return ""

        parts: list[str] = []

        # Parent comment (one level up)
        parent = data.get("parent")
        if parent and parent.get("id"):
            p = self._get(parent["id"], "message,from")
            if p and p.get("message"):
                name = p.get("from", {}).get("name", "Someone")
                parts.append(f"[Parent comment by {name}]: {p['message']}")

        # The comment
        msg = data.get("message", "")
        if msg:
            name = data.get("from", {}).get("name", "Someone")
            parts.append(f"[Comment by {name}]: {msg}")

        # Attachment description
        att = data.get("attachment")
        if att and att.get("description"):
            parts.append(f"[Attachment]: {att['description']}")

        return "\n".join(parts)

    def _format_post(self, post: dict) -> str:
        parts: list[str] = []
        author = post.get("from", {}).get("name", "Unknown")
        parts.append(f"[Post by {author}]")

        # Primary text fields (message > caption > description > story)
        msg = post.get("message", "")
        caption = post.get("caption", "")
        description = post.get("description", "")
        story = post.get("story", "")

        if msg:
            parts.append(msg)
        if caption:
            parts.append(f"Caption: {caption}")
        if description:
            parts.append(f"Description: {description}")
        if story and not msg:
            parts.append(f"(Shared) {story}")

        # Attachment descriptions
        for att in post.get("attachments", {}).get("data", []):
            if att.get("description"):
                parts.append(f"[Attachment]: {att['description']}")
            for sub in att.get("subattachments", {}).get("data", []):
                if sub.get("description"):
                    parts.append(f"[Photo]: {sub['description']}")

        # If nothing at all was extracted → image/video only post
        if len(parts) == 1:
            has_picture = bool(post.get("full_picture"))
            parts.append("Image/Video Post (no text detected)" if has_picture else "Post with no readable content")

        return "\n".join(parts)


fb_service = FacebookService()
