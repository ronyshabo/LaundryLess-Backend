from firebase import db

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