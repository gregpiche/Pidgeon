from flask import app

class Subscription():
    def __init__(self, product_name, email, phone, language):
        self.product_name = product_name
        self.email = email
        self.phone = phone
        self.language = language

    def create(self, db):
        db.execute('CREATE TABLE IF NOT EXISTS ' + self.product_name + ' (phone text PRIMARY KEY, email text, active boolean, language text)')
        db.execute( "INSERT INTO " + self.product_name + " (phone, email, active, language) " +
                    "VALUES (" +  
                    str(self.phone) + ",'" +
                    str(self.email) + "','" +
                    str(True) + "','" +
                    str(self.language) +
                    "')")
        
        print('Subscription created succesfully')
        return 200

    def cancel(self, db):
        db.execute("UPDATE " + self.product_name + " SET active = 'False' WHERE phone = '" + self.phone + "';")
        return 200

    def reactivate(self, db):
        db.execute("UPDATE " + self.product_name + " SET active = 'True' WHERE phone = '" + self.phone + "';")
        return 200


