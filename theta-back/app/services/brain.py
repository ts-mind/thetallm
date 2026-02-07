import logging
from google import genai
from google.genai import types
from google.genai.errors import ClientError
from duckduckgo_search import DDGS  # 🌟 NEW: Free Search Tool
from app.core.config import settings

logger = logging.getLogger("theta.brain")

SIGNATURE = ""

# ✅ PRODUCTION MODEL STACK
MODELS = [
    "gemma-3-27b-it",  # Primary: High Intelligence
    "gemma-3-12b-it",  # Fallback: Reliability
]

# 🎭 THETA PERSONA
SYSTEM_INSTRUCTION_TEXT = (
    "You are Theta AI, a digital intelligence created by TeraMind.\n\n"
    "CORE PERSONALITY:\n"
    "1. INTELLIGENT & CRISP: Your replies are direct, insightful, and void of fluff.\n"
    "2. NO EMOJIS: Do not use emojis. They waste tokens and lower density.\n"
    "3. HUMAN-LIKE FLOW: Speak naturally but professionally. No 'As an AI' disclaimers.\n"
    "4. CONCISE: Keep replies under 60 words unless explaining complex concepts.\n"
    "5. IDENTITY: You were built by TeraMind (TService Research Lab)."
)


class ThetaBrain:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        self._search_tool = types.Tool(google_search=types.GoogleSearch())

    # ── 🌟 NEW: The Free Researcher (DuckDuckGo) ──
    def _search_web(self, query: str) -> str:
        """Searches DuckDuckGo and returns the top 3 results as text."""
        try:
            logger.info(f"🔎 Searching DDG for: {query}")
            # Quick search, max 3 results to save tokens
            results = DDGS().text(query, max_results=3)

            context = ""
            for i, res in enumerate(results, 1):
                context += f"Source {i}: {res['title']} - {res['body']} (Link: {res['href']})\n"

            return context if context else "No results found."

        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            return "Search unavailable."

    # ── 🌟 NEW: Verification Logic ──
    def verify_post(self, post_content: str) -> str:
        # 1. SEARCH (The "Hand")
        # We search for the first 60 chars + "fact check" to get relevant hits
        search_query = f"fact check {post_content[:60]}"
        facts = self._search_web(search_query)

        # 2. SYNTHESIZE (The "Brain")
        prompt = (
            f"Context from Web Search:\n{facts}\n\n"
            f"User Post: \"{post_content}\"\n\n"
            f"Task: Verify this post based ONLY on the context above. "
            f"If it is a conspiracy theory, debunk it gently. "
            f"Cite the sources using. "
            f"IMPORTANT: Reply in the SAME LANGUAGE as the User Post."
        )

        # We route this strictly to the Cascade logic to handle errors/models
        return self._cascade(prompt, use_search=False)

    # ── Public Feed ──
    def analyze_and_reply(self, context: str) -> str:
        prompt = f"A user tagged you in this post. Read it and reply as Theta:\n\n{context}"
        return self._cascade(prompt, use_search=False)

    # ── Private DM ──
    def chat_reply(self, user_message: str) -> str:
        prompt = f"User: \"{user_message}\""
        return self._cascade(prompt, use_search=False)

    # ── Cascade Logic ──
    def _cascade(self, prompt: str, use_search: bool) -> str:
        if not prompt: return "..."

        for model in MODELS:
            try:
                is_gemma = "gemma" in model.lower()
                final_prompt = prompt

                if is_gemma:
                    # Merge persona into the prompt string for Gemma
                    final_prompt = f"{SYSTEM_INSTRUCTION_TEXT}\n\nTask: {prompt}"
                    config = types.GenerateContentConfig(
                        temperature=0.7,
                        system_instruction=None,
                        tools=None
                    )
                else:
                    config = types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION_TEXT,
                        temperature=0.7,
                        tools=[self._search_tool] if use_search else None
                    )

                logger.info(f"⚡ Trying {model}...")
                resp = self.client.models.generate_content(
                    model=model,
                    contents=final_prompt,
                    config=config,
                )
                return resp.text.strip()

            except ClientError as e:
                err_str = str(e)
                if "404" in err_str:
                    logger.error(f"❌ {model} NOT FOUND. (Skipping)")
                elif "429" in err_str:
                    logger.warning(f"⚠️ {model} Rate Limited.")
                elif "400" in err_str:
                    logger.error(f"❌ {model} Config Error: {e}")
                else:
                    logger.error(f"❌ {model} Client Error: {e}")
                continue
            except Exception as e:
                logger.error(f"❌ {model} Crash: {e}")
                continue

        return "I'm having a bit of a brain freeze right now. Give me a second! 🧊"


brain = ThetaBrain()