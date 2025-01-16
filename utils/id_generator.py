from firebase import db

def generate_id(prefix, counter_name, padding):
    counter_ref = db.collection('counters').document(counter_name)
    counter_doc = counter_ref.get()
    
    current_id = counter_doc.to_dict().get('current_id', 0) + 1 if counter_doc.exists else 1
    counter_ref.set({'current_id': current_id})

    return f"{prefix}{str(current_id).zfill(padding)}"

# Specific ID Generators
def generate_user_id():
    return generate_id('USER', 'user_counter', 4)

def generate_driver_id():
    return generate_id('DRIVER', 'driver_counter', 4)

def generate_admin_id():
    return generate_id('ADMIN', 'admin_counter', 4)

def generate_order_id():
    return generate_id('ORDER', 'order_counter', 6)

def generate_garment_id():
    return generate_id('GARM', 'garment_counter', 5)

# test sending to master