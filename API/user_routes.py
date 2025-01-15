from flask import Blueprint, request, jsonify
from firebase_admin import auth
from flasgger import swag_from
from models.user import User
from app import db

# Initialize Blueprint for User routes
user_bp = Blueprint('user_bp', __name__)

# Helper function to generate sequential userID
def generate_user_id():
    counter_ref = db.collection('counters').document('user_counter')
    counter_doc = counter_ref.get()
    if counter_doc.exists:
        current_id = counter_doc.to_dict().get('current_id', 0) + 1
    else:
        current_id = 1
    counter_ref.set({'current_id': current_id})
    return f"USER{str(current_id).zfill(4)}"

# Endpoint to register a new user
@user_bp.route('/user_register', methods=['POST'])
@swag_from({
    'tags': ['User'],
    'summary': 'Register a new user',
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
        201: {'description': 'User account created successfully'},
        400: {'description': 'Error occurred during user registration'}
    }
})
def register_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')
    phone_number = data.get('phone_number')

    try:
        user_record = auth.create_user(email=email, password=password)
        user_id = generate_user_id()  # Generate sequential user ID
        user_instance = User(user_id=user_id, email=email)  # Use User model
        user_data = {
            'user_id': user_instance.user_id,
            'email': user_instance.email,
            'full_name': full_name,
            'phone_number': phone_number,
            'role': 'user'
        }
        db.collection('users').document(user_record.uid).set(user_data)
        return jsonify({'message': 'User account created successfully', 'uid': user_record.uid, 'user_id': user_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Endpoint to login a user
@user_bp.route('/user_login', methods=['POST'])
@swag_from({
    'tags': ['User'],
    'summary': 'Login a user',
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
        200: {'description': 'User logged in successfully'},
        400: {'description': 'Invalid credentials'}
    }
})
def login_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required.'}), 400

    try:
        user = auth.get_user_by_email(email)
        user_doc = db.collection('users').document(user.uid).get()

        if user_doc.exists:
            return jsonify({'message': f'User {email} logged in successfully', 'uid': user.uid}), 200
        else:
            return jsonify({'error': 'User profile not found.'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 400
