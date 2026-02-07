import logging
from google import genai
from google.genai import types
from google.genai.errors import ClientError
from app.core.config import settings

logger = logging.getLogger("theta.brain")

SIGNATURE = "\n\n— Theta AI (TeraMind) 🧬"

# 🛑 STRICT TESTING MODE: GEMMA 3 1B ONLY
# 15,000 RPM (Requests Per Minute) - Virtually unkillable for text.
MODELS = [
    "gemma-3-1b-it",
]

# Simple, direct personality for the 1B model.
# Complex instructions confuse small models, so we keep it very basic.
SYSTEM_CHAT = (
    "You are Theta, a helpful AI assistant.\n"
    "Reply to the user in a friendly, concise way.\n"
    "Keep replies under 50 words."
)


class ThetaBrain:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        # Search tool defined but NOT used for Gemma 1B
        self._search_tool = types.Tool(google_search=types.GoogleSearch())

    # ── Public Feed (Simple Reply) ──
    def analyze_and_reply(self, context: str) -> str:
        prompt = f"Reply to this post context:\n\n{context}"
        return self._cascade(SYSTEM_CHAT, prompt, use_search=False)

    # ── Private DM (Simple Chat) ──
    def chat_reply(self, user_message: str) -> str:
        prompt = f"User said: \"{user_message}\""
        return self._cascade(SYSTEM_CHAT, prompt, use_search=False)

    # ── Cascade Logic ──
    def _cascade(self, system: str, prompt: str, use_search: bool) -> str:
        if not prompt: return "..."

        for model in MODELS:
            try:
                # 🛡️ GEMMA SAFETY PROTOCOL
                # Gemma models (especially small ones) DO NOT support Search Tools.
                # We force tools=[] to prevent "Tool Not Supported" crashes.

                config = types.GenerateContentConfig(
                    system_instruction=system,
                    temperature=0.7,  # Slightly creative
                    # NO TOOLS for Gemma 1B
                )

                logger.info(f"⚡ Trying {model} (No Search)...")

                resp = self.client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=config,
                )

                return resp.text.strip()

            except ClientError as e:
                err_str = str(e)
                if "404" in err_str:
                    logger.error(
                        f"❌ {model} NOT FOUND. Check if 'gemma-3-1b-it' is enabled in your Google Cloud project.")
                elif "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    logger.warning(f"⚠️ {model} Rate Limited.")
                else:
                    logger.error(f"❌ {model} Client Error: {e}")
                continue

            except Exception as e:
                logger.error(f"❌ {model} Crash: {e}")
                continue

        return "I am currently overloaded with messages. Please try again later!"


brain = ThetaBrain()