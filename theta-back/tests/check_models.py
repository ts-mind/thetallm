import os
from dotenv import load_dotenv
from google import genai

# Load env
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ No API Key found.")
    exit()

print(f"🔑 Authenticated. Fetching models...")

client = genai.Client(api_key=api_key)

try:
    for m in client.models.list():
        # Just print the name (it is the only guaranteed attribute)
        print(f"• {m.name}")

        # Optional: Print extra details if they exist
        if hasattr(m, 'display_name'):
            print(f"  - Display: {m.display_name}")

except Exception as e:
    print(f"❌ Error: {e}")