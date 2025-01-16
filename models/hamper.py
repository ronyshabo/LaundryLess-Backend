from app import db
import uuid
from google.cloud import firestore
from models.garment import Garment

class Hamper(Garment):
    def __init__(self, customer_id, quantity=1):
        super().__init__(customer_id, 'hamper', 10.0, quantity)  # Correct super() call
        self.max_weight = 20
        self.status = 'pending'
        self.timestamp = firestore.SERVER_TIMESTAMP

    def save_to_db(self):
        db.collection('hampers').document(self.garment_id).set(self.to_dict())

    def to_dict(self):
        data = super().to_dict()
        data['max_weight'] = self.max_weight
        return data