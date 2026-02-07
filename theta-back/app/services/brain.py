import logging
from google import genai
from google.genai import types
from google.genai.errors import ClientError
from app.core.config import settings

logger = logging.getLogger("theta.brain")

SIGNATURE = ""  # removed signature to make it feel more like a real chat

# ✅ VERIFIED MODEL LIST
MODELS = [
    "gemma-3-1b-it",  # Primary: High rate limit, fast
    "gemma-3-4b-it",  # Secondary: Smarter, still Gemma
]

# 🎭 THETA PERSONA (The "Soul" of the Bot)
# 🎭 THETA PERSONA (Updated for Speed & Professionalism)
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

    # ── Public Feed ──
    def analyze_and_reply(self, context: str) -> str:
        # Feed replies need to be a bit more "service-oriented" but still Theta
        prompt = f"A user tagged you in this post. Read it and reply as Theta:\n\n{context}"
        return self._cascade(prompt, use_search=False)

    # ── Private DM ──
    def chat_reply(self, user_message: str) -> str:
        # DMs should feel like a 1-on-1 text message
        prompt = f"User: \"{user_message}\""
        return self._cascade(prompt, use_search=False)

    # ── Cascade Logic ──
    def _cascade(self, prompt: str, use_search: bool) -> str:
        if not prompt: return "..."

        for model in MODELS:
            try:
                is_gemma = "gemma" in model.lower()

                # 🛠️ CONFIG STRATEGY
                # Gemma 3:
                #   1. NO 'system_instruction' param (Merge it into prompt)
                #   2. NO tools (Search causes crash)

                final_prompt = prompt

                if is_gemma:
                    # Merge persona into the prompt string
                    final_prompt = f"{SYSTEM_INSTRUCTION_TEXT}\n\nTask: {prompt}"

                    config = types.GenerateContentConfig(
                        temperature=0.8,  # Slightly higher for more "human" variance
                        system_instruction=None,  # Explicitly None
                        tools=None  # Explicitly None
                    )
                else:
                    # Gemini 2.5: Can handle native system instruction + Tools
                    config = types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION_TEXT,
                        temperature=0.8,
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