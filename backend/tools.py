import json
from datetime import timezone 
import datetime 
import requests
import os

def utc_timestamp():
  dt = datetime.datetime.now(timezone.utc) 
  
  utc_time = dt.replace(tzinfo=timezone.utc) 
  return utc_time.timestamp() 

def sign_in(custom_token):
  _verify_token_url = 'https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyCustomToken'
  body = {'token' : custom_token.decode(), 'returnSecureToken' : True}
  params = {'key' : os.getenv('FIREBASE_API_KEY')}
  resp = requests.request('post', _verify_token_url, params=params, json=body)
  resp.raise_for_status()
  return resp.json().get('idToken')