from flask import request, jsonify
from config import Config
from . import admin_bp
from flasgger import swag_from
import firebase_admin
from firebase_admin import credentials, initialize_app, firestore, auth
from models.user import AdminUser
from app import db
from firebase_admin import firestore

if not firebase_admin._apps:
    cred = credentials.Certificate(Config.FIREBASE_CREDENTIALS)
    initialize_app(cred)

# Helper function to generate sequential driverID
def generate_admin_id():
    counter_ref = db.collection('counters').document('admin_counter')
    counter_doc = counter_ref.get()
    if counter_doc.exists:
        current_id = counter_doc.to_dict().get('current_id', 0) + 1
    else:
        current_id = 1
    counter_ref.set({'current_id': current_id})
    return f"ADMIN{str(current_id).zfill(4)}"

# Admin Registration
@admin_bp.route('/admin_register', methods=['POST'])
@swag_from({
    'tags': ['Admin'],
    'summary': 'Register a new admin',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'email': {'type': 'string'},
                    'password': {'type': 'string'},
                    'full_name': {'type': 'string'},
                    'phone_number': {'type': 'string'}
                },
                'required': ['email', 'password', 'full_name', 'phone_number']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Admin created successfully'
        },
        400: {
            'description': 'Error occurred during admin creation'
        }
    }
})
def register_admin():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')
    phone_number = data.get('phone_number')

    try:
        user_record = auth.create_user(email=email, password=password)
        admin_id = generate_admin_id()  # Generate sequential AdminID
        admin_user = AdminUser(user_id=user_record.uid, email=email)
        admin_data = {
            'admin_id': admin_id,
            'email': email,
            'full_name': full_name,
            'phone_number': phone_number,
            'role': 'admin'
        }
        db.collection('admins').document(user_record.uid).set(admin_data)
        return jsonify({'message': 'Admin created successfully', 'uid': user_record.uid, 'admin_id': admin_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Admin Login
@admin_bp.route('/admin_login', methods=['POST'])
@swag_from({
    'tags': ['Admin'],
    'summary': 'Login an admin',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'email': {'type': 'string'},
                    'password': {'type': 'string'}
                },
                'required': ['email', 'password']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Admin logged in successfully'
        },
        400: {
            'description': 'Invalid credentials'
        }
    }
})
def login_admin():
    data = request.get_json()
    email = data.get('email')

    try:
        user = auth.get_user_by_email(email)
        admin_doc = db.collection('admins').document(user.uid).get()

        if admin_doc.exists:
            return jsonify({'message': f'Admin {email} logged in successfully', 'uid': user.uid}), 200
        else:
            return jsonify({'error': 'Admin profile not found.'}), 404

    except firebase_admin.auth.AuthError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400
