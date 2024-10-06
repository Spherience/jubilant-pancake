import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:http/http.dart' as http;

import 'package:geolocator/geolocator.dart';

import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_core/firebase_core.dart';

class ApiService {
  static final ApiService _instance = ApiService._internal();

  // Private named constructor
  ApiService._internal();

  late final FirebaseApp app;
  late final FirebaseAuth auth;
  late final List<LatLng> coordinates;
  late DateTime firstTimestamp;

  // Factory constructor that returns the same instance
  factory ApiService() {
    return _instance;
  }

  // Initialize the ApiService (set the apiUrl, waiveUrl, and token)
  void initialize({required FirebaseApp app, required FirebaseAuth auth}) {
    this.app = app;
    this.auth = auth;
  }

  final String apiUrl =
      'https://jubilant-pancake-681105030785.us-central1.run.app/api/waive/undefined';
  final String userRoleApiUrl =
      'https://jubilant-pancake-681105030785.us-central1.run.app/api/user_role';
  final String waiveUrl =
      'https://jubilant-pancake-681105030785.us-central1.run.app/api/waive/';
  final String tragectoryBaseUrl =
      'https://jubilant-pancake-681105030785.us-central1.run.app/api/trajectory';
  final String answerWaveUrl =
      'https://jubilant-pancake-681105030785.us-central1.run.app/api/high_five';

  Future<void> postWaiveData() async {
    String authToken = (await auth.currentUser?.getIdToken())!;
    Position userLocation = await getUserLocation();

    final response = await http.post(
      Uri.parse(waiveUrl),
      headers: {
        'accept': 'application/json',
        'Authorization': '$authToken',
        'Content-Type': 'application/json',
      },
      body: json.encode({
        'latitude': userLocation.latitude,
        'longitude': userLocation.longitude,
      }),
    );

    if (response.statusCode == 200) {
      print('Successfully sent waive data');
    } else {
      print(response.statusCode);
      print(response.body);
      throw Exception('Failed to send waive data');
    }
  }

  // Method to fetch data with JWT token
  Future<List<dynamic>> fetchData() async {
    String authToken = (await auth.currentUser?.getIdToken())!;

    print(authToken);

    final response = await http.get(Uri.parse(apiUrl), headers: {
      'accept': 'application/json',
      'Authorization': '$authToken', // Add JWT token here
    });

    if (response.statusCode == 200) {
      // If the server returns a successful response, parse the JSON
      print("response.body");
      print(response.body);
      return json.decode(response.body)["waives"];
    } else {
      // If the server returns an error, throw an exception
      print(response.statusCode);
      print(response.body);
      throw Exception('Failed to load data');
    }
  } // Method to get the user's current GPS location

  // Method to fetch data with JWT token
  Future<String> getUserRole() async {
    String authToken = (await auth.currentUser?.getIdToken())!;

    print(authToken);

    final response = await http.get(Uri.parse(userRoleApiUrl), headers: {
      'accept': 'application/json',
      'Authorization': '$authToken', // Add JWT token here
    });

    if (response.statusCode == 200) {
      // If the server returns a successful response, parse the JSON
      print("USER_ROLE");
      print(response.body);
      return json.decode(response.body)["role"];
    } else {
      // If the server returns an error, throw an exception
      print(response.statusCode);
      print(response.body);
      throw Exception('Failed to load data');
    }
  } // Method to get the user's current GPS location

  LatLng getCoordinateForCurrentTime({
    required List<LatLng> coordinates, // List of LatLng coordinates
    required DateTime
        initialTimestamp, // Timestamp of the first coordinate in the list
    required DateTime
        currentTimestamp, // Current timestamp to calculate the index
    int stepInSeconds = 60, // Step interval in seconds between coordinates
  }) {
    // Calculate the time difference between the current timestamp and initial timestamp
    Duration difference = currentTimestamp.difference(initialTimestamp);

    // Calculate the index based on the difference and step interval
    int index = (difference.inSeconds / stepInSeconds).floor();

    // Ensure the index does not exceed the bounds of the coordinates array
    if (index < 0) {
      index =
          0; // Use the first coordinate if current time is before initial time
    } else if (index >= coordinates.length) {
      index = coordinates.length - 1; // Use the last coordinate if time exceeds
    }

    // Return the coordinate at the calculated index
    return coordinates[index];
  }

  Future<List<LatLng>> getTrajectoryData() async {
    int startTime = DateTime.now().millisecondsSinceEpoch ~/ 1000;
    firstTimestamp = DateTime.fromMillisecondsSinceEpoch(startTime * 1000);
    int endTime = DateTime.now()
            .add(const Duration(minutes: 90))
            .millisecondsSinceEpoch ~/
        1000;
    int step = 1; //seconds that is

    final String trajectoryUrl =
        '$tragectoryBaseUrl?start_time=$startTime&end_time=$endTime&step=$step';

    String authToken = (await auth.currentUser?.getIdToken())!;
    print(authToken);
    final response = await http.get(
      Uri.parse(trajectoryUrl),
      headers: {
        'accept': 'application/json',
        'Authorization': '$authToken',
      },
    );

    if (response.statusCode == 200) {
      Map<String, dynamic> trajectory = json.decode(response.body);
      List<dynamic> locations = trajectory['locations'];
      late List<LatLng> locationsLatLng = [];

      for (var coord in locations) {
        locationsLatLng.add(LatLng(coord[0], coord[1]));
      }

      coordinates = locationsLatLng;
      return coordinates;
    } else {
      print(response.statusCode);
      print(response.body);
      throw Exception('Failed to load trajectory data');
    }
  }

  Future<LatLng> getCurrentIssCoordinates() async {
    DateTime currentTimestamp = DateTime.now();
    print(firstTimestamp);

    LatLng currentCoordinate = getCoordinateForCurrentTime(
      coordinates: coordinates,
      initialTimestamp: firstTimestamp,
      currentTimestamp: currentTimestamp,
      stepInSeconds: 60,
    );

    print("Current coordinate: $currentCoordinate");

    return currentCoordinate;
  }

  Future<Position> getUserLocation() async {
    bool serviceEnabled;
    LocationPermission permission;

    // Check if location services are enabled
    serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      throw Exception('Location services are disabled.');
    }

    permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) {
        throw Exception('Location permissions are denied');
      }
    }

    if (permission == LocationPermission.deniedForever) {
      throw Exception('Location permissions are permanently denied');
    }

    // Get the current position
    return await Geolocator.getCurrentPosition();
  }

  Future<void> answerWave(String id) async {
    final String answerWaveFullUrl = '$answerWaveUrl/$id';

    String authToken = (await auth.currentUser?.getIdToken())!;
    print(authToken);
    final response = await http.post(
      Uri.parse(answerWaveFullUrl),
      headers: {
        'accept': 'application/json',
        'Authorization': '$authToken',
      },
    );

    if (response.statusCode == 200) {
      print(response.statusCode);
      print(response.body);
    } else {
      print(response.statusCode);
      print(response.body);
      throw Exception('Failed to send high five data');
    }
  }
}
