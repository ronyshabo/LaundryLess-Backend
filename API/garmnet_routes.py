from flask import Blueprint, request, jsonify
from utils.id_generator import generate_garment_id
from models.garment import Garment, Hamper
from firebase import db
from flasgger import swag_from
from utils.garment_prices import GARMENT_PRICE_MAP
import re

garment_bp = Blueprint('garment_bp', __name__)

######################################## 2️ Order a Hamper ########################################
@garment_bp.route('/order_hamper', methods=['POST'])
@swag_from({
    'tags': ['Garment'],
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
            hamper.save_to_db()
            hampers.append(hamper.to_dict())
        return jsonify({
            'message': f'{quantity} hamper(s) ordered successfully',
            'hampers': hampers
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 400


####################################### Update Hamper Price Based on Weight #######################################
@garment_bp.route('/update_hamper_price', methods=['PUT'])
@swag_from({
    'tags': ['Garment'],
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
    
    ##################################### Create a hamper  #######################################
@garment_bp.route('/create_hamper', methods=['POST'])
@swag_from({
    'tags': ['Hamper'],
    'summary': 'Create a new hamper and save it to the database',
    'parameters': [
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
        400: {'description': 'Invalid input or error creating hamper'}
    }
})
def create_hamper():
    data = request.get_json()
    quantity = data.get('quantity', 1)

    # Automatically retrieve the customer ID (e.g., from headers or session)
    customer_id = request.headers.get('Customer-ID')

    if not customer_id:
        return jsonify({'error': 'Customer ID is missing in headers.'}), 400
    if quantity <= 0:
        return jsonify({'error': 'Quantity must be greater than 0.'}), 400

    try:
        hampers = []

        for _ in range(quantity):
            # Generate a unique hamper ID
            hamper_id = generate_garment_id()

            # Create a hamper instance
            hamper = Hamper(hamper_id, customer_id)
            hamper.save_to_db()
            hampers.append(hamper.to_dict())

        return jsonify({
            'message': f'{quantity} hamper(s) created successfully.',
            'hampers': hampers
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 400