# backend/app/services/brain.py
from google import genai
from google.genai import types
from app.core.config import settings

class ThetaBrain:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)

    def analyze_and_reply(self, post_text: str) -> str:
        """
        Uses Google Gemini with Search Grounding to verify a post.
        """
        if not post_text:
            return "Error: No text provided."

        prompt = f"""
        You are Theta, a research AI entity from TeraMind Labs.
        
        TASK: Analyze this viral Facebook post for accuracy.
        POST CONTENT: "{post_text}"
        
        INSTRUCTIONS:
        1. Use Google Search to verify the claims.
        2. If false/misleading: Debunk it with a "Wait a minute..." tone.
        3. If true: Add a technical insight or "Easter egg" fact.
        4. Be concise (max 80 words).
        5. CITE YOUR SOURCES.
        """

        try:
            response = self.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())]
                )
            )
            
            # Add signature
            return f"{response.text}\n\n— Verified by Theta (TeraMind Labs) 🧬"
            
        except Exception as e:
            print(f"Brain Freeze: {e}")
            return "I am currently recalibrating my neural net. Please try again later. — Theta"

brain = ThetaBrain()