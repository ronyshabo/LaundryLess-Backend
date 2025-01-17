from firebase import db
from flasgger import swag_from
from flask import request, jsonify
from . import garment_bp, hamper_bp
from models.garment import Hamper, Garment
from utils.garment_prices import GARMENT_PRICE_MAP
from utils.id_generator import generate_garment_id

######################################## Create a Dry Cleaning Garment ########################################

@garment_bp.route('/create_dry_cleaning_garment', methods=['POST'])
@swag_from({
    'tags': ['Admin'],
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
        garment_id = generate_garment_id()
        # Validate garment name
        if not garment_name or garment_name.lower() not in GARMENT_PRICE_MAP:
            return jsonify({'error': 'Invalid or unsupported garment name.'}), 400

        # Save to 'garments' collection with garment_id
        garment = Garment(name=garment_name, garment_id=garment_id)
        db.collection('garments').document(garment_id).set(garment.to_dict())

        return jsonify({
            'message': 'Dry cleaning garment created successfully',
            'garment': garment.to_dict()
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 400

######################################## Order a Hamper ########################################

@hamper_bp.route('/order_hamper', methods=['POST'])
@swag_from({
    'tags': ['Order'],
    'summary': 'Order a hamper bag with a max weight of 20 lbs',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'customer_id': {'type': 'string'},
                    'quantity': {'type': 'integer'}
                },
                'required': ['customer_id']
            }
        }
    ],
    'responses': {
        201: {'description': 'Hamper ordered successfully'},
        400: {'description': 'Invalid input or error ordering hamper'}
    }
})
def order_hamper():
    data = request.get_json()
    customer_id = data.get('customer_id')
    quantity = data.get('quantity', 1)

    if not customer_id or quantity <= 0:
        return jsonify({'error': 'Invalid customer ID or quantity'}), 400

    try:
        hampers = []
        for _ in range(quantity):
            # Corrected Hamper initialization
            hamper = Hamper(customer_id=customer_id, quantity=1)
            hamper.save_hamper_to_db()
            hampers.append(hamper.to_dict())
        return jsonify({
            'message': f'{quantity} hamper(s) ordered successfully',
            'hampers': hampers
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 400


############################# Update Hamper Price Based on Weight ###############

@hamper_bp.route('/update_hamper_price', methods=['PUT'])
@swag_from({
    'tags': ['Admin'],
    'summary': 'Update hamper price based on its weight',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'hamper_id': {'type': 'string'},
                    'weight': {'type': 'number'}
                },
                'required': ['hamper_id', 'weight']
            }
        }
    ],
    'responses': {
        200: {'description': 'Hamper price updated successfully'},
        400: {'description': 'Invalid input or error updating price'},
        404: {'description': 'Hamper not found'}
    }
})
def update_hamper_price():
    data = request.get_json()
    hamper_id = data.get('hamper_id')
    weight = data.get('weight')

    if not hamper_id or weight is None or weight <= 0:
        return jsonify({'error': 'Invalid hamper ID or weight'}), 400

    try:
        hamper_doc = db.collection('garments').document(hamper_id).get()

        if not hamper_doc.exists:
            return jsonify({'error': 'Hamper not found'}), 404

        # Base price is $10, additional $2 per lb over 10 lbs
        base_price = 10.0
        extra_price = 2.0 * max(0, weight - 10)
        updated_price = base_price + extra_price

        # Update the hamper price in Firestore
        db.collection('garments').document(hamper_id).update({'price': updated_price})

        return jsonify({
            'message': 'Hamper price updated successfully',
            'updated_price': updated_price
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400