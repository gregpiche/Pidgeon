from flask import app

class Subscription():
    def __init__(self, product_name, email, phone, language, first_name, magic_link, is_active, activation_date, cancel_date):
        self.first_name = first_name
        self.product_name = product_name
        self.email = email
        self.phone = phone
        self.language = language
        self.magic_link = magic_link
        self.is_active = is_active
        self.activation_date = activation_date
        self.cancel_date = cancel_date


    def create(self, db):
        db.execute('CREATE TABLE IF NOT EXISTS ' + self.product_name + ' (phone text PRIMARY KEY, email text, isActive boolean, language text, activationDate date, cancelDate date, firstName text, magicLink text)')
        db.execute( "INSERT INTO " + self.product_name + " (phone, email, isActive, language, activationDate, cancelDate, firstName, magicLink) " +
                    "VALUES (" +  
                    str(self.phone) + ",'" +
                    str(self.email) + "','" +
                    str(True) + "','" +
                    str(self.language) + "','" +
                    str(self.activation_date) + "'," + 
                    "null" + ",'" + 
                    str(self.first_name) + "','" +
                    str(self.magic_link) +
                    "')")
        
        print('Subscription created succesfully')
        return 200

    def cancel(self, db):
        db.execute("UPDATE " + self.product_name + " SET active = 'False' WHERE phone = '" + self.phone + "';")
        return 200

    def reactivate(self, db):
        db.execute("UPDATE " + self.product_name + " SET active = 'True' WHERE phone = '" + self.phone + "';")
        return 200


