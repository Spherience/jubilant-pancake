from flask import Flask, request, jsonify
import os
from flasgger import Swagger
from config import Config
import json
import tools
from firebase_admin import auth, db
import firebase_admin
from functools import wraps

app = Flask(__name__)
app.config.from_object(Config)

# Swagger configuration
swagger_config = {
    "securityDefinitions": {
        "BearerAuth": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: 'Authorization: {token}'"
        }
    },
    "security": [
        {
            "BearerAuth": []
        }
    ]
}

swagger = Swagger(app, template=swagger_config)

# Middleware to check authentication
def authenticate_user(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"message": "Token missing"}), 403

        try:
            # Verify the Firebase token
            decoded_token = auth.verify_id_token(token)
            request.user = decoded_token  # Store user info for later use
            
            # Check if user has a role in Firebase Realtime Database
            ref = db.reference(f'roles/{decoded_token["uid"]}')
            user_role = ref.get()
            if not user_role:
                # If the user has no role, assign them the default 'earthling' role
                ref.set({"role": "earthling"})
                request.user_role = "earthling"
            else:
                request.user_role = user_role.get("role", "earthling")
            
        except Exception as e:
            return jsonify({"message": "Invalid token"}), 403

        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper
  
# Middleware to check for admin role
def admin_required(func):
    @authenticate_user
    def wrapper(*args, **kwargs):
        user = request.user

        ref = db.reference(f'roles/{user["uid"]}')
        user_role = ref.get()

        if user_role and user_role.get('role') == 'admin':
            return func(*args, **kwargs)
        else:
            return jsonify({"message": "Admin access required"}), 403
    wrapper.__name__ = func.__name__
    return wrapper

@app.route('/api/data', methods=['GET'])
@authenticate_user
def get_data():
    """
    Get data from Firebase Realtime Database
    ---
    responses:
      200:
        description: A successful response
    """
    ref = db.reference('data')
    data = ref.get()
    return jsonify(data), 200

@app.route('/api/data', methods=['POST'])
@admin_required
def add_data():
    """
    Add data to Firebase Realtime Database (Admin Only)
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
    ref = db.reference('data')
    ref.push(data)  # Push the data to the 'data' node
    return jsonify({"message": "Data added successfully"}), 200

@app.route('/api/users', methods=['GET'])
# @admin_required
def get_all_users():
    """
    Get all users from Firebase Authentication (Admin Only)
    ---
    responses:
      200:
        description: List of users
    """
    users = []
    page = auth.list_users()
    while page:
        for user in page.users:
            # Fetch role from Realtime Database
            ref = db.reference(f'roles/{user.uid}')
            user_role = ref.get()
            role = user_role.get("role", "user") if user_role else "user"
            users.append({
                "uid": user.uid,
                "email": user.email,
                "display_name": user.display_name,
                "role": role
            })
        page = page.get_next_page()

    return jsonify(users), 200

@app.route('/api/users/role', methods=['POST'])
# @admin_required
def change_user_role():
    """
    Change user role in Firebase Realtime Database (Admin Only)
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          id: RoleChange
          properties:
            uid:
              type: string
            role:
              type: string
    responses:
      200:
        description: Role changed successfully
    """
    data = request.json
    user_uid = data.get('uid')
    new_role = data.get('role')

    if not user_uid or not new_role:
        return jsonify({"message": "Invalid data"}), 400

    # Update the user's role in Realtime Database
    ref = db.reference(f'roles/{user_uid}')
    ref.set({"uid": user_uid, "role": new_role})
    
    return jsonify({"message": f"Role changed to {new_role} for user {user_uid}"}), 200
  
@app.route("/api/token/<string:user_id>", methods=["GET"])
def generate_token(user_id):
  """
  Generate auth token
  ---
  parameters:
      - name: user_id
        in: path
        type: string
        required: true
        description: user id
  responses:
    200:
      description: List of users
  """
  user = auth.get_user(user_id)
  
  return user.getIdToken(), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
