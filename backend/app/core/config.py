# backend/app/core/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Theta LLM Backend"
    VERSION: str = "1.0.0"
    
    # Secrets
    FB_PAGE_ACCESS_TOKEN: str = os.getenv("FB_PAGE_ACCESS_TOKEN")
    FB_VERIFY_TOKEN: str = os.getenv("FB_VERIFY_TOKEN")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    
    # Facebook Graph API URL
    FB_GRAPH_URL: str = "https://graph.facebook.com/v19.0"

settings = Settings()