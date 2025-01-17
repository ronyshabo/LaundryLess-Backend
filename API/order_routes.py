
from app import db
from flasgger import swag_from
from flask import Blueprint, request, jsonify


order_bp = Blueprint('order_bp', __name__)


@order_bp.route('/add_to_cart', methods=['POST'])
@swag_from({
    'tags': ['Order'],
    'summary': 'Add a garment to the user’s cart',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'user_id': {'type': 'string'},
                    'garment_id': {'type': 'string'},
                    'quantity': {'type': 'integer'}
                },
                'required': ['user_id', 'garment_id']
            }
        }
    ],
    'responses': {
        200: {'description': 'Garment added to cart successfully'},
        404: {'description': 'Garment not found'},
        400: {'description': 'Error adding garment to cart'}
    }
})
def add_to_cart():
    data = request.get_json()
    user_id = data.get('user_id')          # Custom User ID (e.g., USER0001)
    garment_id = data.get('garment_id')
    quantity = data.get('quantity', 1)

    try:
        # Step 1: Find the Firestore Document ID for the given user_id
        user_query = db.collection('users').where('user_id', '==', user_id).limit(1).stream()
        user_doc = next(user_query, None)

        if not user_doc:
            return jsonify({'error': 'User not found.'}), 404

        firestore_user_id = user_doc.id  # Get the Firestore-generated document ID

        # Step 2: Fetch the garment details
        garment_doc = db.collection('garments').document(garment_id).get()
        if not garment_doc.exists:
            return jsonify({'error': 'Garment not found.'}), 404

        garment_data = garment_doc.to_dict()
        garment_data['quantity'] = quantity
        garment_data['total_price'] = garment_data['price'] * quantity

        # Step 3: Add the garment to the user's cart
        db.collection('users').document(firestore_user_id).collection('cart_items').document(garment_id).set(garment_data)

        return jsonify({'message': 'Garment added to cart successfully.'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
@order_bp.route('/remove_from_cart', methods=['DELETE'])   
@swag_from({
    'tags': ['Order'],
    'summary': 'Remove a garment from the user’s cart',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'user_id': {'type': 'string'},
                    'garment_id': {'type': 'string'}
                },
                'required': ['user_id', 'garment_id']
            }
        }
    ],
    'responses': {
        200: {'description': 'Garment removed from cart'},
        404: {'description': 'Garment not found in cart'},
        400: {'description': 'Error removing garment'}
    }
})
def remove_from_cart():
    data = request.get_json()
    user_id = data.get('user_id')
    garment_id = data.get('garment_id')

    try:
        # Remove garment from user's cart
        cart_item = db.collection('users').document(user_id).collection('cart_items').document(garment_id).get()
        if not cart_item.exists:
            return jsonify({'error': 'Garment not found in cart.'}), 404

        db.collection('users').document(user_id).collection('cart_items').document(garment_id).delete()

        return jsonify({'message': 'Garment removed from cart successfully.'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400