from flask import Flask, request, jsonify
import os
from flasgger import Swagger
from config import Config
import json
import tools
from firebase_admin import auth, db
import firebase_admin
from functools import wraps
import datetime
import iss_tools

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
  
@app.route('/api/waive/<string:location>', methods=['GET'])
@authenticate_user
def get_waives(location = ""):
  """
    Post location info with geolocation (latitude and longitude)
    ---
    parameters:
      - name: location
        in: path
        required: false
        schema:
          id: Geolocation
          properties:
            latitude:
              type: number
              description: Latitude of the location
              required: true
            longitude:
              type: number
              description: Longitude of the location
              required: true
    responses:
      200:
        description: List of waive objects
    """
    
  latitude = None
  longitude = None
  
  if location and location != "undefined":
    loc = json.loads(location)
    latitude = loc["latitude"]
    longitude = loc["longitude"]
    
  ref = db.reference('waives')
  waives = ref.get()
  
  resp = [{**{"id": id}, **waives[id]} for id in waives]
  
  return jsonify(resp), 200
  

@app.route('/api/waive/', methods=['POST'])
@authenticate_user
def send_waive():
    """
    Post location info with geolocation (latitude and longitude)
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          id: Geolocation
          properties:
            latitude:
              type: number
              description: Latitude of the location
              required: true
            longitude:
              type: number
              description: Longitude of the location
              required: true
    responses:
      200:
        description: A successful response with location info
      400:
        description: Missing or invalid parameters
    """
    
    data = request.get_json()

    # Get latitude and longitude from JSON body
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    if latitude is None or longitude is None:
        return jsonify({"message": "Latitude and longitude are required"}), 400

    try:
        latitude = float(latitude)
        longitude = float(longitude)
        default_photo = "https://firebasestorage.googleapis.com/v0/b/nasa-space-apps-challeng-b676a.appspot.com/o/usr.png?alt=media&token=c87c8c80-6b01-40c4-b7b3-6862a677ad32"
        # Example response: You can customize this to return data based on geolocation
        location_data = {
            # "id": ,
            "user": {
              "uid": request.user["uid"],
              "name": request.user["display_name"] if "display_name" in request.user else "Some earthling",
              "photo": request.user["photoURL"] if "photoURL" in request.user else default_photo
            },
            "latitude": latitude,
            "longitude": longitude,
            "utc_timestamp": tools.utc_timestamp()
        }
        
        ref = db.reference('waives')
        ref.push(location_data)
  
        return "", 200

    except Exception as e:
        return jsonify({"message": "Invalid latitude or longitude values"}), 400
  
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
  # user = auth.get_user(user_id)
  token = auth.create_custom_token(user_id)
  
  id_token = tools.sign_in(token)
  
  return id_token, 200

@app.route('/api/trajectory', methods=['GET'])
@authenticate_user
def get_trajectory():
    """
    Create ISS movement prediction
    ---
    parameters:
      - name: start_time
        in: query
        type: number
        required: false
        description: Range start time in UTC, POSIX time
      - name: end_time
        in: query
        type: number
        required: false
        description: Range end time in UTC, POSIX time
      - name: step
        in: query
        type: number
        required: false
        description: Step duration in seconds
    responses:
      200:
        description: Successful trajectory prediction
        schema:
          type: object
          properties:
            trajectory:
              type: array
              items:
                type: object
                properties:
                  time:
                    type: number
                    description: Time in POSIX format
                  position:
                    type: object
                    properties:
                      lat:
                        type: number
                        description: Latitude of the ISS
                      lon:
                        type: number
                        description: Longitude of the ISS
    """
    try:
        # Get start_time from query, default to current UTC time
        start_time = request.args.get('start_time')
        start_time = datetime.datetime.fromtimestamp(float(start_time)) if start_time else datetime.datetime.now(datetime.timezone.utc)

        # Get end_time from query, default to 90 minutes after start_time
        end_time = request.args.get('end_time')
        end_time = datetime.datetime.fromtimestamp(float(end_time)) if end_time else start_time + datetime.timedelta(minutes=90)

        # Get step from query, default to 60 seconds
        step = request.args.get('step')
        step = datetime.timedelta(seconds=int(step)) if step else datetime.timedelta(seconds=60)

        # Generate trajectory using iss_tools
        trajectory_data = iss_tools.getTrajectory(start_time, end_time, step)
        return jsonify({
            "timestamp_posix": start_time.timestamp(),
            "step_seconds": step.seconds,
            "locations": [[l[0],l[1]] for l in trajectory_data]
        }), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)