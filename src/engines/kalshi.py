import requests
import datetime
import base64
from urllib.parse import urlparse
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
import uuid

demo = True

api_key_id = ["08a25890-a8fa-4e96-a105-f133a36bde34", "4beb2212-be89-4f64-b02b-fa7cf5ce5b5e"]
api_key_id = api_key_id[1] if demo else api_key_id[0]

class Kalshi:
    def __init__(self, key_path, api_key_id, demo = True):
        self.key_path = key_path
        self.private_key= self.load_private_key()
        self.api_key_id = api_key_id
        self.url = "https://external-api.demo.kalshi.co/trade-api/v2" if demo else "https://external-api.kalshi.com/trade-api/v2" 
    
    def load_private_key(self):
        with open(self.key_path, "rb") as f:
            return serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())
    
    def create_headers(api_key_id, signature, timestamp):
        headers = {
            'KALSHI-ACCESS-KEY': api_key_id,
            'KALSHI-ACCESS-SIGNATURE': signature,
            'KALSHI-ACCESS-TIMESTAMP': timestamp
        }
        return headers
    
    def sign_request(self, timestamp, method, path):
        message = f"{timestamp}{method}{path}".encode('utf-8')
        
        signature = self.private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.DIGEST_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode('utf-8')
    
    def create_payload(side, count):
        payload = {
            'ticker': None,
            "client_order_id": str(uuid.uuid4()),
            'side': side,
            'count': count,
            'price': '0.99' if side == 'bid' else '0.01',
            'time_in_force': 'immediate_or_cancel',
            "self_trade_prevention_type": "taker_at_cross",
            "exchange_index": -1
        }
        return payload

    def post(self, path, payload):
        full_path = f"/trade-api/v2{path}"

        timestamp = str(int(datetime.datetime.now().timestamp() * 1000))        
        signature = self.sign_request(self.private_key, timestamp, "POST", full_path)
        headers = self.create_headers(self.api_key_id, signature, timestamp)
        headers['Content_Type'] = 'application/json'
        
        return requests.post(self.url+full_path, headers=headers, json=payload)

    def get(self, path):
        full_path = f"/trade-api/v2{path}"
        
        timestamp = str(int(datetime.datetime.now().timestamp() * 1000)) 
        signature = self.sign_request(self.private_key, timestamp, "GET", full_path)
        headers = self.create_headers(self.api_key_id, signature, timestamp)
        
        return requests.get(self.url+full_path, headers=headers)


    


path = "/portfolio/events/orders"

test = Kalshi('data/speed-2.pem', '4beb2212-be89-4f64-b02b-fa7cf5ce5b5e')


