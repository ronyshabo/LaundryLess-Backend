import re
from app import db
from . import user_bp
from flasgger import swag_from
from firebase_admin import auth
from flask import request, jsonify
from models.user import User, CreditCard
from utils.id_generator import generate_user_id, generate_credit_card_id


# Endpoint to register a new user
@user_bp.route('/user_register', methods=['POST'])
@swag_from({
    'tags': ['User'],
    'summary': 'Admin-only:Register a new user',
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
        user_id = generate_user_id() # Generate sequential user ID
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

# Endpoint to update user information, including address using user_id
@user_bp.route('/update_user_info', methods=['PUT'])
@swag_from({
    'tags': ['User'],
    'summary': 'Update user profile information and address using user_id',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'user_id': {'type': 'string'},  # Changed from 'uid' to 'user_id'
                    'full_name': {'type': 'string'},
                    'phone_number': {'type': 'string'},
                    'address': {'type': 'string'},
                    'address2': {'type': 'string'},
                    'city': {'type': 'string'},
                    'state': {'type': 'string'},
                    'zip_code': {'type': 'string'}
                },
                'required': ['user_id', 'full_name', 'phone_number', 'address', 'city', 'state', 'zip_code']
            }
        }
    ],
    'responses': {
        200: {'description': 'User profile updated successfully'},
        400: {'description': 'Invalid input or error updating profile'},
        404: {'description': 'User not found'}
    }
})
def update_user_info():
    data = request.get_json()
    user_id = data.get('user_id')
    full_name = data.get('full_name')
    phone_number = data.get('phone_number')
    address = data.get('address')
    address2 = data.get('address2', '')
    city = data.get('city')
    state = data.get('state')
    zip_code = data.get('zip_code')

    # Validation for state (2-letter abbreviation)
    if not state or not re.match(r'^[A-Za-z]{2}$', state):
        return jsonify({'error': 'Invalid state format. Provide a 2-letter abbreviation.'}), 400

    # Validation for ZIP code (5 digits or ZIP+4)
    if not zip_code or not re.match(r'^\d{5}(-\d{4})?$', zip_code):
        return jsonify({'error': 'Invalid ZIP code format. Provide a 5-digit ZIP or ZIP+4.'}), 400

    try:
        # Query user by 'user_id' instead of document ID
        user_query = db.collection('users').where('user_id', '==', user_id).stream()
        user_docs = [doc for doc in user_query]

        if not user_docs:
            return jsonify({'error': 'User not found.'}), 404

        # Get the Firestore document ID for the matched user
        user_doc_id = user_docs[0].id

        # Prepare updated data
        updated_data = {
            'full_name': full_name,
            'phone_number': phone_number,
            'address_details': {
                'address': address,
                'address2': address2,
                'city': city,
                'state': state.upper(),
                'zip_code': zip_code
            }
        }

        # Update user document in Firestore
        db.collection('users').document(user_doc_id).update(updated_data)

        return jsonify({'message': f'User {user_id} profile updated successfully.'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
# Endpoint to add credit card information for a user
@user_bp.route('/add_credit_card', methods=['POST'])
@swag_from({
    'tags': ['User'],
    'summary': 'Add credit card information to user profile (CVV not stored)',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'user_id': {'type': 'string'},
                    'cardholder_name': {'type': 'string'},
                    'card_number': {'type': 'string'},
                    'expiration_date': {'type': 'string'},  # MM/YY
                    'billing_address': {'type': 'string'}
                },
                'required': ['user_id', 'cardholder_name', 'card_number', 'expiration_date', 'billing_address']
            }
        }
    ],
    'responses': {
        200: {'description': 'Credit card added successfully'},
        400: {'description': 'Invalid input or error adding credit card'},
        404: {'description': 'User not found'}
    }
})
def add_credit_card():
    data = request.get_json()
    user_id = data.get('user_id')
    cardholder_name = data.get('cardholder_name')
    card_number = data.get('card_number')
    expiration_date = data.get('expiration_date')
    billing_address = data.get('billing_address')

    # Validate card number (basic check)
    if not re.match(r'^\d{13,19}$', card_number):
        return jsonify({'error': 'Invalid card number. Must be 13-19 digits.'}), 400

    # Validate expiration date (MM/YY)
    if not re.match(r'^(0[1-9]|1[0-2])\/\d{2}$', expiration_date):
        return jsonify({'error': 'Invalid expiration date format. Use MM/YY.'}), 400

    try:
        # Query user by 'user_id'
        user_query = db.collection('users').where('user_id', '==', user_id).stream()
        user_docs = [doc for doc in user_query]

        if not user_docs:
            return jsonify({'error': 'User not found.'}), 404

        # Get the Firestore document ID
        user_doc_id = user_docs[0].id

        # Generate unique credit card ID
        credit_card_id = generate_credit_card_id()

        # Initialize credit card model
        credit_card = CreditCard(
            cardholder_name=cardholder_name,
            card_number=card_number,
            expiration_date=expiration_date,
            billing_address=billing_address,
            credit_card_id=credit_card_id
        )

        # Save the credit card to the user's subcollection in Firestore
        db.collection('users').document(user_doc_id).collection('credit_cards').document(credit_card_id).set(credit_card.to_dict())

        return jsonify({'message': 'Credit card added successfully.'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400
