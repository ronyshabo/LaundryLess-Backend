# partner.py
from google.cloud import firestore

class Partner:
    def __init__(self, partner_id, name, partner_type, address, city, state, zip_code, contact_info, status='active'):
        self.partner_id = partner_id
        self.name = name
        self.partner_type = partner_type  # 'laundromat' or 'apartment_complex'
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.contact_info = contact_info
        self.status = status  # 'active' or 'inactive'
        self.created_at = firestore.SERVER_TIMESTAMP
        self.updated_at = firestore.SERVER_TIMESTAMP
    
    def to_dict(self):
        return {
            'partner_id': self.partner_id,
            'name': self.name,
            'partner_type': self.partner_type,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'contact_info': self.contact_info,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }