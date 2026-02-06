# backend/app/services/facebook.py
import requests
from app.core.config import settings


class FacebookService:
    """
    Handles all Facebook Graph API interactions.
    Implements the "Context Fetch" strategy: walking up the post/comment tree
    to gather full context before the AI generates a reply.
    """

    def _graph_get(self, endpoint: str, params: dict) -> dict:
        """Helper: make an authenticated GET request to the Graph API."""
        params["access_token"] = settings.FB_PAGE_ACCESS_TOKEN
        url = f"{settings.FB_GRAPH_URL}/{endpoint}"
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Graph API GET error for {endpoint}: {e}")
            return {}

    # ------------------------------------------------------------------
    # CONTEXT FETCHING — "Walk Up the Tree"
    # ------------------------------------------------------------------

    def get_post_context(self, post_id: str) -> str:
        """
        Fetches full context for a post. This is the core "context fetch" logic.
        
        Strategy:
        1. Try fetching the object as a POST first (message, story, type, attachments).
        2. If it's actually a COMMENT, fetch the comment text + its parent post.
        3. Combine everything into a context string for the LLM.
        """
        # First, try to get it as a post
        post_data = self._graph_get(post_id, {
            "fields": "message,story,type,created_time,from,attachments{description,media,subattachments}"
        })

        if not post_data or "error" in post_data:
            # It might be a comment ID — try fetching as a comment
            return self._get_comment_context(post_id)

        return self._format_post_context(post_data)

    def _get_comment_context(self, comment_id: str) -> str:
        """
        Fetches a comment and walks up to its parent post for full context.
        """
        # Fetch the comment itself
        comment_data = self._graph_get(comment_id, {
            "fields": "message,from,created_time,parent,attachment"
        })

        if not comment_data or "error" in comment_data:
            print(f"⚠️ Could not fetch comment: {comment_id}")
            return ""

        comment_text = comment_data.get("message", "")
        parent = comment_data.get("parent")

        # If this comment has a parent (i.e., it's a reply to another comment),
        # walk up to the parent comment
        parent_context = ""
        if parent and parent.get("id"):
            parent_data = self._graph_get(parent["id"], {
                "fields": "message,from,created_time"
            })
            parent_msg = parent_data.get("message", "")
            parent_from = parent_data.get("from", {}).get("name", "Unknown")
            if parent_msg:
                parent_context = f"[Parent Comment by {parent_from}]: {parent_msg}\n"

        # Now try to get the root post this comment belongs to
        # The post_id is embedded in the comment_id format: {post_id}_{comment_id}
        root_post_context = ""
        if "_" in comment_id:
            root_post_id = comment_id.split("_")[0] + "_" + comment_id.split("_")[1] if comment_id.count("_") >= 2 else comment_id.rsplit("_", 1)[0]
            # Actually, Facebook comment IDs are formatted as {page_id}_{comment_id}
            # The post_id we need is different. Let's just try fetching via object metadata.
            pass

        context_parts = []
        if parent_context:
            context_parts.append(parent_context)
        if comment_text:
            comment_from = comment_data.get("from", {}).get("name", "Unknown")
            context_parts.append(f"[Comment by {comment_from}]: {comment_text}")

        # Fetch attachment descriptions if any
        attachment = comment_data.get("attachment")
        if attachment:
            desc = attachment.get("description", "")
            if desc:
                context_parts.append(f"[Attachment Description]: {desc}")

        return "\n".join(context_parts) if context_parts else ""

    def _format_post_context(self, post_data: dict) -> str:
        """
        Formats a post's data into a clean context string for the LLM.
        """
        context_parts = []

        # Post author
        author = post_data.get("from", {}).get("name", "Unknown")
        context_parts.append(f"[Post by {author}]")

        # Post message (the main text content)
        message = post_data.get("message", "")
        if message:
            context_parts.append(f"Content: {message}")

        # Story (for share-type posts like "X shared a link")
        story = post_data.get("story", "")
        if story and not message:
            context_parts.append(f"Story: {story}")

        # Attachment descriptions (images, links, videos)
        attachments = post_data.get("attachments", {}).get("data", [])
        for att in attachments:
            desc = att.get("description", "")
            if desc:
                context_parts.append(f"[Attachment]: {desc}")
            
            # Check sub-attachments (e.g., photo albums)
            sub_atts = att.get("subattachments", {}).get("data", [])
            for sub in sub_atts:
                sub_desc = sub.get("description", "")
                if sub_desc:
                    context_parts.append(f"[Sub-Attachment]: {sub_desc}")

        return "\n".join(context_parts) if context_parts else ""

    # ------------------------------------------------------------------
    # SIMPLE FETCHERS (kept for backward compatibility)
    # ------------------------------------------------------------------

    def get_post_content(self, post_id: str) -> str:
        """Fetches just the text content of a specific post (simple version)."""
        data = self._graph_get(post_id, {"fields": "message"})
        return data.get("message", "")

    # ------------------------------------------------------------------
    # ACTIONS
    # ------------------------------------------------------------------

    def post_comment(self, object_id: str, message: str):
        """Replies to a post or comment."""
        url = f"{settings.FB_GRAPH_URL}/{object_id}/comments"
        params = {
            "message": message,
            "access_token": settings.FB_PAGE_ACCESS_TOKEN
        }
        try:
            r = requests.post(url, params=params, timeout=10)
            r.raise_for_status()
            print(f"✅ Replied to {object_id}")
            return r.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to reply to {object_id}: {e}")
            return None


fb_service = FacebookService()
