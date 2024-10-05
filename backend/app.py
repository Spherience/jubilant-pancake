from flask import Flask, request
from pymongo import MongoClient
import os
from flasgger import Swagger
from config import Config
import json
import tools

app = Flask(__name__)
app.config.from_object(Config)

# Swagger configuration
swagger = Swagger(app)

# MongoDB connection
uri = os.getenv("MONGO_URI")
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DB_NAME")]

@app.route('/api/data', methods=['GET'])
def get_data():
    """
    Get data from the database
    ---
    responses:
      200:
        description: A successful response
    """
    try:
      data = list(db.data_collection.find())

      return tools.json_fy(data), 200
    
    except Exception as e:
      return tools.json_fy(e), 500
      

@app.route('/api/data', methods=['POST'])
def add_data():
    """
    Add data to the database
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          id: Data
          properties:
            key:
              type: string
            value:
              type: string
    responses:
      200:
        description: Data added successfully
    """
    data = request.json
    db.data_collection.insert_one(data)
    return tools.json_fy({"message": "Data added successfully"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
