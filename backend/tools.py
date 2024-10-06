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

def create_user_from_req(request):
  
  default_photo = "https://firebasestorage.googleapis.com/v0/b/nasa-space-apps-challeng-b676a.appspot.com/o/usr.png?alt=media&token=c87c8c80-6b01-40c4-b7b3-6862a677ad32"
  return {
    "uid": request.user["uid"],
    "name": request.user["display_name"] if "display_name" in request.user else "Some earthling",
    "photo": request.user["photoURL"] if "photoURL" in request.user else default_photo
  }