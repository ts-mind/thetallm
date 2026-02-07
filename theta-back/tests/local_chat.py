import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 1. Setup
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ Error: GOOGLE_API_KEY not found.")
    sys.exit(1)

client = genai.Client(api_key=api_key)

# 2. Config
MODEL_ID = "gemma-3-1b-it"  # The model we found in your list
print(f"🧬 Connecting to {MODEL_ID}...")
print("Type 'quit' or 'exit' to stop.\n")

# 3. Chat Loop
# We maintain a simple history string for context (since 1B models have short memory)
chat_history = "System: You are a helpful, concise AI assistant.\n"

while True:
    try:
        # Get User Input
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit"]:
            print("Exiting...")
            break

        # Append to history
        chat_history += f"User: {user_input}\nModel: "

        # Send to API (Zero Config to prevent 400 Errors)
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=chat_history,
            config=types.GenerateContentConfig(
                temperature=0.7,
                system_instruction=None,  # Explicitly disabled
                tools=None  # Explicitly disabled
            )
        )

        reply = response.text.strip()
        print(f"Theta: {reply}\n")

        # Append reply to history so it remembers
        chat_history += f"{reply}\n"

    except Exception as e:
        print(f"❌ Error: {e}")