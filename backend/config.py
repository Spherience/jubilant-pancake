import os
from dotenv import main

main.load_dotenv()

class Config:
    SWAGGER = {
        'title': 'Flask API',
        'uiversion': 3
    }
    MONGO_URI = os.getenv('MONGO_URI')
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME')