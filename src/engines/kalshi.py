import requests
import datetime
import base64
from urllib.parse import urlparse
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
import uuid
import asyncio
import json


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
    
    def get_events(self, series_ticker=None, event_ticker=None, limit=None, status=None, tickers=None):
        params = {}
        if series_ticker:
            params['series_ticker'] = series_ticker.upper()
        if event_ticker:
            params['event_ticker'] = event_ticker.upper()
        if limit:
            params['limit'] = limit
        if status:
            params['status'] = status
        if tickers:
            params['tickers'] = tickers
        if series_ticker:
            tail = "/events"
        elif event_ticker:
            tail = '/markets'
        return self.get('/events', params)
    
    
    async def create_event_name_map(self, series_ticker, limit, map_prompt):
        from engines.fast_scraper import ask_ai
        events = self.get_events(series_ticker=series_ticker, limit=limit)
        responce = events.json()
        name_to_event_ticker = {}
        for event in responce['events']:
            print(event['title'])
            print(event['event_ticker'])
            name = await ask_ai(f'{map_prompt} {event['title']}')
            name_to_event_ticker[name.upper()] = event['event_ticker']
        return name_to_event_ticker
        

