from flask import Blueprint, request, jsonify
from firebase_admin import auth
from flasgger import swag_from
from models.user import DriverUser
from app import db


# Initialize Blueprint for Driver routes
driver_bp = Blueprint('driver_bp', __name__)


# Helper function to generate sequential driverID
def generate_driver_id():
    counter_ref = db.collection('counters').document('driver_counter')
    counter_doc = counter_ref.get()
    if counter_doc.exists:
        current_id = counter_doc.to_dict().get('current_id', 0) + 1
    else:
        current_id = 1
    counter_ref.set({'current_id': current_id})
    return f"DRIVER{str(current_id).zfill(4)}"

# Endpoint to register a new driver
@driver_bp.route('/driver_register', methods=['POST'])
@swag_from({
    'tags': ['Driver'],
    'summary': 'Register a new driver',
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
                    'phone_number': {'type': 'string'},
                    'vehicle_type': {'type': 'string'},
                    'license_plate': {'type': 'string'}
                },
                'required': ['email', 'password', 'full_name', 'phone_number', 'vehicle_type', 'license_plate']
            }
        }
    ],
    'responses': {
        201: {'description': 'Driver account created successfully'},
        400: {'description': 'Error occurred during driver registration'}
    }
})
def register_driver():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')
    phone_number = data.get('phone_number')
    vehicle_type = data.get('vehicle_type')
    license_plate = data.get('license_plate')

    try:
        user_record = auth.create_user(email=email, password=password)
        driver_id = generate_driver_id()  # Generate sequential driver ID
        driver_data = {
            'driver_id': driver_id,
            'email': email,
            'full_name': full_name,
            'phone_number': phone_number,
            'vehicle_type': vehicle_type,
            'license_plate': license_plate,
            'role': 'driver'
        }
        db.collection('drivers').document(user_record.uid).set(driver_data)
        return jsonify({'message': 'Driver account created successfully', 'uid': user_record.uid, 'driver_id': driver_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Endpoint to retrieve driver profile
@driver_bp.route('/driver/<driver_id>', methods=['GET'])
@swag_from({
    'tags': ['Driver'],
    'summary': 'Retrieve driver profile by ID',
    'parameters': [
        {
            'name': 'driver_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'Unique ID of the driver'
        }
    ],
    'responses': {
        200: {'description': 'Driver profile retrieved successfully'},
        404: {'description': 'Driver not found'}
    }
})
def get_driver_profile(driver_id):
    try:
        doc = db.collection('drivers').document(driver_id).get()
        if doc.exists:
            driver_data = doc.to_dict()
            user_record = auth.get_user(driver_data['uid'])
            return jsonify(user_record), 200
        else:
            return jsonify({'error': 'Driver not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Endpoint to login a driver
@driver_bp.route('/driver_login', methods=['POST'])
@swag_from({
    'tags': ['Driver'],
    'summary': 'Login a driver',
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
        200: {'description': 'Driver logged in successfully'},
        400: {'description': 'Invalid credentials'}
    }
})
def login_driver():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required.'}), 400

    try:
        user = auth.get_user_by_email(email)
        driver_doc = db.collection('drivers').document(user.uid).get()

        if driver_doc.exists:
            return jsonify({'message': f'Driver {email} logged in successfully', 'uid': user.uid}), 200
        else:
            return jsonify({'error': 'Driver profile not found.'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 400
