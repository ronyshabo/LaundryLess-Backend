import re
from firebase import db
from datetime import datetime

class User:
    def __init__(self, user_id, email):
        self.user_id = user_id
        self.email = email

    def get_profile(self):
        doc = db.collection('users').document(self.user_id).get()
        if doc.exists:
            return doc.to_dict()
        return None

    def update_profile(self, data):
        db.collection('users').document(self.user_id).update(data)
        return "Profile updated successfully."

class CustomerUser(User):
    def __init__(self, user_id, email):
        super().__init__(user_id, email)
        self.role = 'customer'

    def view_orders(self):
        orders = db.collection('orders').where('customer_id', '==', self.user_id).stream()
        return [order.to_dict() for order in orders]

    def create_order(self, order_details):
        order_data = {
            'customer_id': self.user_id,
            'order_details': order_details,
            'status': 'pending',
            'created_at': datetime.utcnow()
        }
        order_ref = db.collection('orders').add(order_data)
        return f"Order {order_ref[1].id} created successfully."
    
    def update_address(self, address, address2, city, state, zip_code):
        # Validate state (must be a 2-letter abbreviation)
        if not re.match(r'^[A-Za-z]{2}$', state):
            return "Invalid state format. Please provide a 2-letter state abbreviation."

        # Validate ZIP code (5 digits or 5+4 format)
        if not re.match(r'^\d{5}(-\d{4})?$', zip_code):
            return "Invalid ZIP code format. Please provide a 5-digit ZIP code or ZIP+4."

        # Update address in Firestore
        address_data = {
            'address': address,
            'address2': address2,
            'city': city,
            'state': state.upper(),
            'zip_code': zip_code
        }
        db.collection('users').document(self.user_id).update({'address_details': address_data})
        return "Address updated successfully."
    
class AdminUser(User):
    def __init__(self, user_id, email):
        super().__init__(user_id, email)
        self.role = 'admin'

    def view_all_users(self):
        users = db.collection('users').stream()
        return [user.to_dict() for user in users]

    def delete_user(self, target_user_id):
        db.collection('users').document(target_user_id).delete()
        return f"User {target_user_id} has been deleted."

class DriverUser(User):
    def __init__(self, user_id, email):
        super().__init__(user_id, email)
        self.role = 'driver'

    def view_assigned_deliveries(self):
        deliveries = db.collection('deliveries').where('driver_id', '==', self.user_id).stream()
        return [delivery.to_dict() for delivery in deliveries]

    def update_delivery_status(self, delivery_id, status):
        db.collection('deliveries').document(delivery_id).update({'status': status})
        return f"Delivery {delivery_id} status updated to {status}."

class CreditCard:
    def __init__(self, cardholder_name, card_number, expiration_date, billing_address):
        self.cardholder_name = cardholder_name
        self.card_number = self.mask_card_number(card_number)
        self.expiration_date = expiration_date
        self.billing_address = billing_address
        self.added_at = datetime.utcnow()

    @staticmethod
    def mask_card_number(card_number):
        return f"{'*' * (len(card_number) - 4)}{card_number[-4:]}"

    def to_dict(self):
        return {
            'cardholder_name': self.cardholder_name,
            'card_number': self.card_number,
            'expiration_date': self.expiration_date,
            'billing_address': self.billing_address,
            'added_at': self.added_at
        }