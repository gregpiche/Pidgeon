from flask import app

class Subscription():
    def __init__(self, order_id, email, phone, created_at, sku):
        self.order_id = order_id
        self.email = email
        self.phone = phone
        self.created_at = created_at
        self.sku = sku.replace('-', '')


    def create(self, db):
        db.execute('CREATE TABLE IF NOT EXISTS ' + self.sku + ' (order_id bigint PRIMARY KEY, email text, phone text, created_at date)')
        db.execute( "INSERT INTO " + self.sku + " (order_id, email, phone, created_at) " +
                    "VALUES (" +  
                    str(self.order_id) + ",'" +
                    str(self.email) + "','" +
                    str(self.phone) + "','" +
                    str(self.created_at.split('T')[0]) +
                    "')")
        
        return 200

    def delete_object(self):
        return 200


