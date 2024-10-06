from flask import Flask, request, jsonify
import os
from flasgger import Swagger
from config import Config
import json
import tools
from firebase_admin import auth, db
import datetime
import iss_tools
import roles

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
  
@app.route('/api/waive/<string:location>', methods=['GET'])
@roles.authenticate_user
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
  waives = waives if waives else []
  
  ref = db.reference('high_fives')
  high_fives = ref.get()
  high_fives = high_fives if high_fives else []
  
  resp = {
    "waives": [{**{"id": id}, **waives[id]} for id in waives],
    "high_fives": [{**{"id": id}, **high_fives[id]} for id in high_fives]
  }
  
  return jsonify(resp), 200
  

@app.route('/api/waive/', methods=['POST'])
@roles.authenticate_user
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
@roles.authenticate_user
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

@app.route('/api/next_pass_over/', methods=['POST'])
@roles.authenticate_user
def next_pass_over():
    """
    Find next passover closest location and time
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
            longitude:
              type: number
              description: Longitude of the location
        required:
          - latitude
          - longitude
    responses:
      200:
        description: Successful response with next passover time and location
        schema:
          type: object
          properties:
            timestamp:
              type: number
              description: Timestamp of the next ISS passover (POSIX time)
            latitude:
              type: number
              description: Latitude of the ISS at the passover time
            longitude:
              type: number
              description: Longitude of the ISS at the passover time
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
        # Convert latitude and longitude to float
        latitude = float(latitude)
        longitude = float(longitude)

        # Call to iss_tools to find the next passover
        next_pass = iss_tools.nextPassOver(latitude, longitude, datetime.datetime.now(datetime.timezone.utc))
        pass_time = next_pass.midpoint

        # Get ISS location at that passover time
        location = iss_tools.getIssLocation(pass_time)

        return jsonify({
            "timestamp": pass_time.timestamp(),  # Convert datetime to POSIX timestamp
            "latitude": location[0],             # Latitude of the ISS
            "longitude": location[1]             # Longitude of the ISS
        }), 200

    except ValueError:
        # If the latitude or longitude cannot be converted to a float
        return jsonify({"message": "Latitude and longitude must be valid numbers"}), 400
    except Exception as e:
        # Handle other unforeseen errors
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500
      
@app.route('/api/high_five/<string:waive_id>', methods=['POST'])
@roles.astronaut_required
def send_high_five(waive_id):
    """
    Send a high five to a specific waive
    ---
    parameters:
      - name: waive_id
        in: path
        required: true
        type: string
        description: The ID of the waive receiving the high five
    responses:
      200:
        description: High five successfully sent
        content:
          application/json:
            schema:
              type: object
              properties:
                waive:
                  type: object
                  description: Details of the waive receiving the high five
                astronaut:
                  type: object
                  description: Details of the astronaut sending the high five
                  properties:
                    id:
                      type: string
                      description: ID of the astronaut
                    name:
                      type: string
                      description: Name of the astronaut
                iss_latitude:
                  type: number
                  description: Latitude of the ISS at the time of the high five
                iss_longitude:
                  type: number
                  description: Longitude of the ISS at the time of the high five
                utc_timestamp:
                  type: number
                  description: UTC timestamp of the high five in POSIX time
      400:
        description: Waive not found or invalid input
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Error message indicating the waive was not found
    """
    
    ref = db.reference(f'waives/{waive_id}')
    waive = ref.get()
    
    if not waive:
        return jsonify({"message": "Waive not existing"}), 400

    ref = db.reference('high_fives')
    latitude, longitude = iss_tools.getIssLocation(datetime.datetime.now(datetime.timezone.utc))
    
    hf = {
        "waive": waive,
        "astronaut": tools.create_user_from_req(request),
        "iss_latitude": latitude,
        "iss_longitude": longitude,
        "utc_timestamp": tools.utc_timestamp()
    }
    
    ref.push(hf)
    
    return jsonify(hf), 200
  
@app.route('/api/user_role', methods=['GET'])
@roles.authenticate_user
def get_user_role():
    """
    Get the authenticated user's role
    ---
    responses:
      200:
        description: Returns the authenticated user and their role
        schema:
          type: object
          properties:
            uid:
              type: string
              description: The authenticated user's UID
            email:
              type: string
              description: The authenticated user's email
            role:
              type: string
              description: The authenticated user's role
      403:
        description: Invalid or missing token
    """
    user = request.user  # Extract the user info from request
    role = request.user_role  # Extract the user's role from request
    
    return jsonify({
        "uid": user.get("uid"),
        "email": user.get("email"),
        "role": role
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)