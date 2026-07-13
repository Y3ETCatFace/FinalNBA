import requests
import datetime
import base64
from urllib.parse import urlparse
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
import uuid


api_key_id = ["08a25890-a8fa-4e96-a105-f133a36bde34", "4beb2212-be89-4f64-b02b-fa7cf5ce5b5e"]

class Kalshi:
    def __init__(self, key_path, api_key_id, url):
        self.key_path = key_path
        self.private_key= self.load_private_key()
        self.api_key_id = api_key_id
        self.url = url    
    
    def load_private_key(self):
        with open(self.key_path, "rb") as f:
            return serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())
    
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
    
    def create_payload(self, side, count, market_ticker, price):
        payload = {
            'ticker': market_ticker,
            "client_order_id": str(uuid.uuid4()),
            'side': side,
            'count': f'{float(count):.2f}',
            'price': f'{price}',
            'time_in_force': 'immediate_or_cancel',
            "self_trade_prevention_type": "taker_at_cross",
            "exchange_index": -1
        }
        return payload
    
    def create_headers(self, signature, timestamp):
        headers = {
            'KALSHI-ACCESS-KEY': self.api_key_id,
            'KALSHI-ACCESS-SIGNATURE': signature,
            'KALSHI-ACCESS-TIMESTAMP': timestamp
        }
        return headers

    def post(self, path, payload):
        full_path = f"/trade-api/v2{path}"

        timestamp = str(int(datetime.datetime.now().timestamp() * 1000))        
        signature = self.sign_request(timestamp, "POST", full_path)
        headers = self.create_headers(signature, timestamp)
        headers['Content_Type'] = 'application/json'
        
        return requests.post(self.url+full_path, headers=headers, json=payload)

    def get(self, path, params=None):
        full_path = f"/trade-api/v2{path}"
        timestamp = str(int(datetime.datetime.now().timestamp() * 1000)) 
        signature = self.sign_request(timestamp, "GET", full_path)
        headers = self.create_headers(signature, timestamp)
        
        return requests.get(self.url+full_path, headers=headers, params=params)
    
    def create_order(self, market_ticker, side, amount, price):
        payload = self.create_payload(side, amount, market_ticker, price)
        message = self.post("/portfolio/events/orders", payload)
        return message
    
    def get_events(self, series_ticker, limit=None, status=None, tickers=None):
        params = {}
        if series_ticker:
            params['series_ticker'] = series_ticker.upper()
        if limit:
            params['limit'] = limit
        if status:
            params['status'] = status
        if tickers:
            params['tickers'] = tickers
        return self.get('/events', params)
    
    """
    def create_event_name_map(self, series_ticker, describe_action):
        events = self.get_events(series_ticker=series_ticker, limit=20)
        responce = events.json()
        name_to_event_ticker = {}
        for event in responce['events']:
            print(event['title'])
            print(event['event_ticker'])
            name = await ask_ai(f'Only return TWO WORDS A FIRST NAME AND LAST ex. (John Adams) What is the NBA players full name in this title or rather what are the first two words of this sentence what is the name? Dont say anything else just his first and last name from this title I am about to show you: {event["title"]}')
            print(name)
            """
      


