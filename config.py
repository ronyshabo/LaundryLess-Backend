import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")

    # Path to Firebase Admin SDK service account key
    FIREBASE_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json')

    # Pyrebase configuration for Authentication & Database
    FIREBASE_CONFIG = {
        "apiKey": os.getenv("API_KEY"),
        "authDomain": os.getenv("AUTH_DOMAIN"),
        "databaseURL": os.getenv("DATABASE_URL"),
        "projectId": os.getenv("PROJECT_ID"),
        "storageBucket": os.getenv("STORAGE_BUCKET"),
        "messagingSenderId": os.getenv("MESSAGING_SENDER_ID"),
    }

    # Google OAuth 2.0 Credentials for Sign-in
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")