import pyrebase
import firebase_admin
from config import Config
from flask import redirect
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK (for Firestore)
if not firebase_admin._apps:
    cred = credentials.Certificate(Config.FIREBASE_CREDENTIALS)
    firebase_admin.initialize_app(cred)

# Initialize Firestore (Admin SDK)
db = firestore.client()

# Initialize Pyrebase (for Authentication)
firebase = pyrebase.initialize_app(Config.FIREBASE_CONFIG)
auth = firebase.auth()

def create_user_in_firestore(user_id, user_data):
    """Creates a new user document in AUthentication Firestore."""
    db.collection('users').document(user_id).set(user_data)
    return "User created successfully in Firestore."

def google_callback():
    """Handles callback after Google authentication."""
    user = auth.current_user
    if user:
        user_data = {
            "email": user['email'],
            "user_id": user['localId']
        }
        create_user_in_firestore(user['localId'], user_data)
        return f"Logged in as {user['email']}"
    return "No user is currently logged in."

def google_login():
    # Placeholder logic for Google Authentication
    return redirect('https://accounts.google.com/o/oauth2/auth')