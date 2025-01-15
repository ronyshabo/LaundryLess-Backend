# garment_routes.py
from flask import Blueprint, request, jsonify
from firebase_admin import auth
from flasgger import swag_from
from models.garment import Garment
from firebase import db
import uuid
from google.cloud import firestore

garment_bp = Blueprint('garment_bp', __name__)

@garment_bp.route('/add_hamper', methods=['POST'])
@swag_from({
    'tags': ['Garment'],
    'summary': 'Add hampers to a user',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'user_id': {'type': 'string'},
                    'hamper_count': {'type': 'integer'}
                },
                'required': ['user_id']
            }
        }
    ],
    'responses': {
        200: {'description': 'Hampers added successfully'},
        400: {'description': 'Invalid user_id or hamper_count'}
    }
})
def order_hamper():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        hamper_count = data.get('hamper_count', 1)
        
        if not user_id or hamper_count <= 0:
            return jsonify({"error": "Invalid user_id or hamper_count"}), 400
        
        # Create hamper entries
        hampers = []
        for _ in range(hamper_count):
            hamper_id = str(uuid.uuid4())
            hamper = Garment(item_type='hamper', item_id=hamper_id)
            hampers.append(hamper.__dict__)
        
        # Update Firestore user collection
        user_ref = db.collection('users').document(user_id)
        user_ref.update({
            'hampers': firestore.ArrayUnion(hampers)
        })

        return jsonify({"message": f"{hamper_count} hamper(s) added to user {user_id}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# garment.py
from google.cloud import firestore  # Import Firestore to use SERVER_TIMESTAMP

class Garment:
    def __init__(self, item_type, item_id):
        self.item_type = item_type
        self.item_id = item_id
        self.status = 'pending'  # Default status
        self.timestamp = firestore.SERVER_TIMESTAMP