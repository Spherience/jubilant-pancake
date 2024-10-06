from functools import wraps
from flask import request, jsonify
from firebase_admin import auth, db

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
              
            uid = decoded_token["uid"]
            # Check if user has a role in Firebase Realtime Database
            roles_ref = db.reference(f'roles/{uid}')
            user_role = roles_ref.get()
            if not user_role:
                # If the user has no role, assign them the default 'earthling' role
                roles_ref.set({"role": "earthling"})
                request.user_role = "earthling"
            else:
                request.user_role = user_role.get("role", "earthling")
            
        except Exception as e:
            return jsonify({"message": "Invalid token"}), 403

        return func(*args, **kwargs)
    return wrapper

# Middleware to check if user has a specific role
def role_required(role):
    def decorator(func):
        @wraps(func)
        @authenticate_user
        def wrapper(*args, **kwargs):
            user_role = request.user_role
            if user_role == role or user_role == 'admin':
                return func(*args, **kwargs)
            else:
                return jsonify({"message": f"{role.capitalize()} access required"}), 403
        return wrapper
    return decorator

# Middleware for admin access
admin_required = role_required('admin')

# Middleware for astronaut access (including admin access)
astronaut_required = role_required('astronaut')