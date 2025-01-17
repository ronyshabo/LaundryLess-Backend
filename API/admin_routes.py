from app import db
import firebase_admin
from . import admin_bp
from config import Config
from flasgger import swag_from
from models.hamper import Hamper
from models.user import AdminUser
from models.garment import Garment
from flask import request, jsonify
from utils.id_generator import generate_admin_id
from utils.garment_prices import GARMENT_PRICE_MAP
from firebase_admin import credentials, initialize_app, auth


if not firebase_admin._apps:
    cred = credentials.Certificate(Config.FIREBASE_CREDENTIALS)
    initialize_app(cred)

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

@admin_bp.route('/get_all_users', methods=['GET'])
@swag_from({
    'tags': ['Admin'],
    'summary': 'Retrieve all users from the database',
    'responses': {
        200: {'description': 'List of all users'},
        400: {'description': 'Error retrieving users'}
    }
})
def get_all_users():
    try:
        # Fetch all documents in the 'users' collection
        users = db.collection('users').stream()

        user_list = []
        for user in users:
            user_data = user.to_dict()
            print(f"Fetched User: {user_data}")  # Debugging

            # If role doesn't exist, infer role from user_id pattern or assign 'unknown'
            user_id = user_data.get('user_id', 'unknown')
            
            # Infer role from user_id prefix if role is missing
            if 'role' not in user_data:
                if user_id.startswith('USER'):
                    user_data['role'] = 'customer'
                elif user_id.startswith('DRIVER'):
                    user_data['role'] = 'driver'
                elif user_id.startswith('ADMIN'):
                    user_data['role'] = 'admin'
                else:
                    user_data['role'] = 'unknown'

            # Add user to the list
            user_list.append(user_data)

        # Debug if no users found
        if not user_list:
            print("No users found.")  # Debugging

        return jsonify({'users': user_list}), 200

    except Exception as e:
        print(f"Error: {e}")  # Debugging
        return jsonify({'error': str(e)}), 400

# Endpoint to get user by user_id
@admin_bp.route('/get_user/<user_id>', methods=['GET'])
@swag_from({
    'tags': ['Admin'],
    'summary': 'Retrieve a user by user_id',
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'Custom User ID (e.g., USER0001)'
        }
    ],
    'responses': {
        200: {'description': 'User data retrieved successfully'},
        404: {'description': 'User not found'},
        400: {'description': 'Error retrieving user'}
    }
})
def get_user_by_id(user_id):
    try:
        # Query by the 'user_id' field instead of document ID
        user_query = db.collection('users').where('user_id', '==', user_id).stream()
        user_data = [user.to_dict() for user in user_query]

        if user_data:
            return jsonify(user_data[0]), 200
        else:
            return jsonify({'error': 'User not found.'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
    
@admin_bp.route('/create_dry_cleaning_garment', methods=['POST'])
@swag_from({
    'tags': ['Garment'],
    'summary': 'Admin-only: Create a new dry cleaning garment',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'required': True,
            'type': 'string',
            'description': 'Admin user ID for authentication (e.g., ADMIN0001)'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'}
                },
                'required': ['name']
            }
        }
    ],
    'responses': {
        201: {'description': 'Garment created and saved successfully'},
        403: {'description': 'Access denied. Admins only.'},
        400: {'description': 'Invalid input or error creating garment'}
    }
})
def create_dry_cleaning_garment():
    data = request.get_json()
    garment_name = data.get('name')

    # Check if Authorization header is present and starts with ADMIN
    admin_id = request.headers.get('Authorization')

    if not admin_id or not admin_id.startswith('ADMIN'):
        return jsonify({'error': 'Access denied. Only admins can perform this action.'}), 403

    try:
        # Validate garment name
        if not garment_name or garment_name.lower() not in GARMENT_PRICE_MAP:
            return jsonify({'error': 'Invalid or unsupported garment name.'}), 400

        # Save to 'garments' collection
        garment = Garment(name=garment_name)
        garment.save_to_db()

        return jsonify({
            'message': 'Dry cleaning garment created successfully',
            'garment': garment.to_dict()
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
@admin_bp.route('/create_hamper', methods=['POST'])
@swag_from({
    'tags': ['Hamper'],
    'summary': 'Admin-only: Create a new hamper and save it to the database',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'required': True,
            'type': 'string',
            'description': 'Admin user ID for authentication (e.g., ADMIN0001)'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'quantity': {'type': 'integer', 'default': 1}
                }
            }
        }
    ],
    'responses': {
        201: {'description': 'Hamper(s) created and saved successfully'},
        403: {'description': 'Access denied. Admins only.'},
        400: {'description': 'Invalid input or error creating hamper'}
    }
})
def create_hamper():
    data = request.get_json()
    quantity = data.get('quantity', 1)

    # Check if Authorization header is present and starts with ADMIN
    admin_id = request.headers.get('Authorization')

    if not admin_id or not admin_id.startswith('ADMIN'):
        return jsonify({'error': 'Access denied. Only admins can perform this action.'}), 403

    if quantity <= 0:
        return jsonify({'error': 'Quantity must be greater than 0.'}), 400

    try:
        hampers = []

        for _ in range(quantity):
            # Generate a new hamper and save it
            hamper = Hamper(quantity=1)
            hamper.save_to_db()
            hampers.append(hamper.to_dict())

        return jsonify({
            'message': f'{quantity} hamper(s) created successfully.',
            'hampers': hampers
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 400