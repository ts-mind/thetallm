import logging
from google import genai
from google.genai import types
from google.genai.errors import ClientError
from app.core.config import settings

logger = logging.getLogger("theta.brain")

SIGNATURE = "\n\n— Theta AI (TeraMind) 🧬"

# 🛑 STRICT TESTING MODE: GEMMA 3 1B ONLY
MODELS = [
    "gemma-2-2b-it",  # Fallback to 2b if 1b isn't available in your region yet
    "gemma-2-9b-it",  # Stronger fallback
]

# Simple, direct personality for the small model.
SYSTEM_CHAT = (
    "You are Theta, a helpful AI assistant.\n"
    "Reply to the user in a friendly, concise way.\n"
    "Keep replies under 50 words."
)


class ThetaBrain:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        self._search_tool = types.Tool(google_search=types.GoogleSearch())

    # ── Public Feed ──
    def analyze_and_reply(self, context: str) -> str:
        prompt = f"Reply to this post context:\n\n{context}"
        return self._cascade(SYSTEM_CHAT, prompt, use_search=False)

    # ── Private DM ──
    def chat_reply(self, user_message: str) -> str:
        prompt = f"User said: \"{user_message}\""
        return self._cascade(SYSTEM_CHAT, prompt, use_search=False)

    # ── Cascade Logic ──
    def _cascade(self, system: str, prompt: str, use_search: bool) -> str:
        if not prompt: return "..."

        for model in MODELS:
            try:
                is_gemma = "gemma" in model.lower()

                # 🛠️ FIX: Handle System Instructions
                # Gemma API throws 400 if we use 'system_instruction' param.
                # So for Gemma, we merge system rules INTO the prompt.

                final_prompt = prompt
                final_system = system

                if is_gemma:
                    final_system = None
                    final_prompt = f"{system}\n\nTask: {prompt}"

                # Configure Model
                config = types.GenerateContentConfig(
                    system_instruction=final_system,
                    temperature=0.7,
                    # Disable tools for Gemma to prevent crashes
                    tools=[self._search_tool] if (use_search and not is_gemma) else None
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
                    logger.error(f"❌ {model} NOT FOUND. Check your API region/list.")
                elif "400" in err_str:
                    logger.error(f"❌ {model} Config Error: {e}")
                elif "429" in err_str:
                    logger.warning(f"⚠️ {model} Rate Limited.")
                else:
                    logger.error(f"❌ {model} Client Error: {e}")
                continue

            except Exception as e:
                logger.error(f"❌ {model} Crash: {e}")
                continue

        return "I am currently overloaded. Please try again later!"


brain = ThetaBrain()