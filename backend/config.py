import os
from dotenv import main
import firebase_admin
from firebase_admin import credentials, db

main.load_dotenv()

class Config:
    SWAGGER = {
        'title': 'Flask API',
        'uiversion': 3
    }
    
    # Initialize Firebase Admin SDK
    cred = credentials.Certificate(os.getenv('FIREBASE_CREDENTIALS_PATH'))
    firebase_admin.initialize_app(cred, {
        'databaseURL': os.getenv('FIREBASE_DATABASE_URL')
    })