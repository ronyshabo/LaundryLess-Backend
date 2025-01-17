import uuid
from app import db
from utils.garment_prices import GARMENT_PRICE_MAP

class Garment:
    def __init__(self, name, quantity=1):
        self.garment_id = str(uuid.uuid4())
        self.name = name.lower()
        self.price = GARMENT_PRICE_MAP.get(self.name, 0.0)
        self.quantity = quantity
        self.status = 'available'

    def save_to_db(self):
        db.collection('garments').document(self.garment_id).set(self.to_dict())

    def to_dict(self):
        return {
            'garment_id': self.garment_id,
            'name': self.name,
            'price': self.price,
            'quantity': self.quantity,
            'status': self.status,
            'total_price': self.price * self.quantity
        }

class Hamper(Garment):
    def __init__(self, customer_id, quantity=1):
        super().__init__(customer_id, 'hamper', quantity)
        self.price = 10.0
        self.max_weight = 20

    def to_dict(self):
        data = super().to_dict()
        data['max_weight'] = self.max_weight
        return data