import firebase_admin
from firebase_admin import credentials, initialize_app, firestore
from config import Config

# Initialize Firebase only once
if not firebase_admin._apps:
    cred = credentials.Certificate(Config.FIREBASE_CREDENTIALS)
    initialize_app(cred)

# Initialize Firestore
db = firestore.client()