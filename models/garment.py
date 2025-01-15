from app import db

class Garment:
    def __init__(self, garment_id, customer_id, type, price):
        self.garment_id = garment_id
        self.customer_id = customer_id
        self.type = type
        self.price = price

    def save_to_db(self):
        db.collection('garments').document(self.garment_id).set(self.to_dict())

    def to_dict(self):
        return {
            'garment_id': self.garment_id,
            'customer_id': self.customer_id,
            'type': self.type,
            'price': self.price
        }

class Hamper(Garment):
    def __init__(self, garment_id, customer_id):
        super().__init__(garment_id, customer_id, 'Hamper', 20.0)
        self.max_weight = 20

    def to_dict(self):
        data = super().to_dict()
        data['max_weight'] = self.max_weight
        return data