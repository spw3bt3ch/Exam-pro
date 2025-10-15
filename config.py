import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'app.db'}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # External API Configuration
    QUESTIONS_API_BASE_URL = "https://questions.aloc.com.ng/api/v2/q"
    QUESTIONS_API_TOKEN = os.environ.get("QUESTIONS_API_TOKEN", "QB-23b20d59287d87f94d94")
    QUESTIONS_API_HEADERS = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'AccessToken': QUESTIONS_API_TOKEN
    }

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
