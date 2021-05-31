from flask import Flask, request, abort
from model import Subscription
from sqlalchemy import create_engine
import json
import hmac
import hashlib
import base64
import json

SECRET = b'08391bb61db3c364d79aaa912d54217daa05ca740b3638c59de074a9fbedf978'
app = Flask(__name__)
db_string = 'postgresql://ggxrscfguwscxn:2f81ffcdf8567f72c82592fc0d96e4d7a2c94e47d725fb2ed56536c06cc96481@ec2-3-215-57-87.compute-1.amazonaws.com:5432/du9obpspmfelf'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = create_engine(db_string)

def verify_webhook(data, hmac_header):
    digest = hmac.new(SECRET, data, hashlib.sha256).digest()
    computed_hmac = base64.b64encode(digest)

    return hmac.compare_digest(computed_hmac, hmac_header.encode('UTF-8'))

# This is standard functionality to verify incoming requests
#
# @app.route('/webhook', methods=['POST'])
# def handle_webhook():
#     data = request.get_data()
#     verified = verify_webhook(data, request.headers.get('X-Shopify-Hmac-SHA256'))

#     if not verified:
#         abort(401)
#     # process webhook payload
#     # ...

#     return ('Webhook verified', 200)

@app.route('/order-create', methods=['POST', 'GET'])
def order_create():
    data = request.get_data()
    verified = verify_webhook(data, request.headers.get('X-Shopify-Hmac-SHA256'))

    if not verified:
        abort(401)

    if request.method == 'POST':
        content = request.get_json()
        order_id = content['id']
        email = content['email']
        phone = content['billing_address']['phone']
        created_at = content['created_at']
        line_items = content['line_items']

        for item in line_items:
            model = Order.Order(order_id, email, phone, created_at, item['sku'])
            model.create(db)
        
        #json_object = json.loads(json_data)
        #json_formatted_str = json.dumps(request.get_json, indent=2)
        

    return ('Webhook verified', 200)

@app.route('/subscription-start', methods=['POST'])
def subscription_start():
    print(request.get_json())
    return ('Webhook verified', 200)

@app.route('/subscription-cancel', methods=['POST'])
def subscription_cancel():
    print(request.get_json())
    return ('Webhook verified', 200)

@app.route('/subscription-reactivate', methods=['POST'])
def subscription_reactivate():
    print(request.get_json())
    return ('Webhook verified', 200)

if __name__ == "__main__":
    app.run()