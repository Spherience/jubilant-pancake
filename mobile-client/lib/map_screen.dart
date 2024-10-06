import 'dart:async';
import 'dart:ui' as ui;
import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:async';
import 'api_service.dart';

class CustomMapScreen extends StatefulWidget {
  // ignore: public_member_api_docs
  const CustomMapScreen({super.key});

  @override
  // ignore: library_private_types_in_public_api
  _CustomMapScreenState createState() => _CustomMapScreenState();
}

class _CustomMapScreenState extends State<CustomMapScreen> {
  late GoogleMapController _controller;

  Set<Polyline> _polylines = {};
  Set<Marker> _markers = {};

  late List<LatLng> coordinates = [];

  // Define a unique polyline id
  final PolylineId polylineId = PolylineId("route");

  @override
  void initState() {
    super.initState();
  }

  late Marker issMarker;

  // Method to add marker with animation
  Future<void> _setIssMarker(LatLng position) async {
    // Initial marker with smallest icon
    issMarker = await _createMarker(position, 'iss');

    setState(() {
      _markers.add(issMarker);
    });
  }

// Function to create a marker with a given icon
  Future<Marker> _createMarker(LatLng position, String markerId) async {
    final BitmapDescriptor icon = await BitmapDescriptor.fromAssetImage(
      ImageConfiguration(size: Size(48, 48)),
      'assets/iss.png', // Custom marker icon path
    );

    return Marker(
      markerId: MarkerId(markerId),
      position: position,
      infoWindow: InfoWindow(
        title: 'Location: $markerId',
        snippet: 'Lat: ${position.latitude}, Lng: ${position.longitude}',
      ),
      icon: icon,
    );
  }

  Future<void> _addMarkerWithoutAnimation(LatLng position, String id) async {
    // Generate the bitmaps at different scales for the animation
    List<BitmapDescriptor> icons = await Future.wait([
      _createMarkerFromEmoji("👋", 90),
      _createMarkerFromEmoji("👋", 85),
      _createMarkerFromEmoji("👋", 80),
      _createMarkerFromEmoji("👋", 75),
      _createMarkerFromEmoji("👋", 70),
      _createMarkerFromEmoji("👋", 65),
      _createMarkerFromEmoji("👋", 70),
      _createMarkerFromEmoji("👋", 75),
      _createMarkerFromEmoji("👋", 80),
      _createMarkerFromEmoji("👋", 85),
      _createMarkerFromEmoji("👋", 90),
    ]);

    // Initial marker with smallest icon
    Marker marker = Marker(
      markerId: MarkerId(id),
      position: position,
      icon: icons[0],
      onTap: () async {
        ApiService apiService = ApiService();
        String userRole = await apiService.getUserRole();
        print("YOOOOOOOOOOOOOOOOOOOOOO $userRole");
        if (userRole == "astronaut") {
          apiService.answerWave(id);
          _updateMarkerWithAnimation(position, id);
        } else {

        }
        // Handle marker tap
        //_showMarkerInfo(context, position);
      },
    );

    setState(() {
      _markers.add(marker);
    });

    // Animate by updating the marker icon
    int index = 0;
    Timer.periodic(Duration(milliseconds: 60), (timer) {
      if (index >= icons.length) {
        timer.cancel();
      } else {
        setState(() {
          _markers.removeWhere((m) => m.markerId == marker.markerId);
          marker = marker.copyWith(
            iconParam: icons[index],
          );
          _markers.add(marker);
        });
        index++;
      }
    });
  }


  Future<void> _updateMarkerWithAnimation(LatLng position, String id) async {
    // Generate the bitmaps at different scales for the animation
    List<BitmapDescriptor> icons = await Future.wait([
      _createMarkerFromEmoji("👋", 90),
      _createMarkerFromEmoji("👋", 75),
      _createMarkerFromEmoji("👋", 55),
      _createMarkerFromEmoji("👋", 35),
      _createMarkerFromEmoji("👋", 15),
      _createMarkerFromEmoji("👋", 5),
      _createMarkerFromEmoji("🙌", 5),
      _createMarkerFromEmoji("🙌", 15),
      _createMarkerFromEmoji("🙌", 35),
      _createMarkerFromEmoji("🙌", 55),
      _createMarkerFromEmoji("🙌", 75),
      _createMarkerFromEmoji("🙌", 90),
    ]);
    // Initial marker with smallest icon
    Marker marker = Marker(
      markerId: MarkerId(id),
      position: position,
      icon: icons[0],
    );

    setState(() {
      _markers.add(marker);
    });

    // Animate by updating the marker icon
    int index = 0;
    Timer.periodic(Duration(milliseconds: 60), (timer) {
      if (index >= icons.length) {
        timer.cancel();
      } else {
        setState(() {
          _markers.removeWhere((m) => m.markerId == marker.markerId);
          marker = marker.copyWith(
            iconParam: icons[index],
          );
          _markers.add(marker);
        });
        index++;
      }
    });
  }


  Future<void> _addMarkerWithAnimation(LatLng position) async {
    // Generate the bitmaps at different scales for the animation
    List<BitmapDescriptor> icons = await Future.wait([
      _createMarkerFromEmoji("👋", 90),
      _createMarkerFromEmoji("👋", 85),
      _createMarkerFromEmoji("👋", 80),
      _createMarkerFromEmoji("👋", 75),
      _createMarkerFromEmoji("👋", 70),
      _createMarkerFromEmoji("👋", 65),
      _createMarkerFromEmoji("👋", 70),
      _createMarkerFromEmoji("👋", 75),
      _createMarkerFromEmoji("👋", 80),
      _createMarkerFromEmoji("👋", 85),
      _createMarkerFromEmoji("👋", 90),
    ]);

    // Initial marker with smallest icon
    Marker marker = Marker(
      markerId: MarkerId('new'),
      position: position,
      icon: icons[0],
    );

    setState(() {
      _markers.add(marker);
    });

    // Animate by updating the marker icon
    int index = 0;
    Timer.periodic(Duration(milliseconds: 60), (timer) {
      if (index >= icons.length) {
        timer.cancel();
      } else {
        setState(() {
          _markers.removeWhere((m) => m.markerId == marker.markerId);
          marker = marker.copyWith(
            iconParam: icons[index],
          );
          _markers.add(marker);
        });
        index++;
      }
    });
  }

  // Method to create a marker with emoji text (👋) converted to a bitmap image
  Future<BitmapDescriptor> _createMarkerFromEmoji(String emoji,
      double fontSize) async {
    final textPainter = TextPainter(
      textDirection: TextDirection.ltr,
      text: TextSpan(
        text: emoji,
        style: TextStyle(fontSize: fontSize, color: Colors.black),
      ),
    );

    textPainter.layout();
    final pictureRecorder = ui.PictureRecorder();
    final canvas = Canvas(pictureRecorder);
    textPainter.paint(canvas, Offset(0, 0));
    final picture = pictureRecorder.endRecording();
    final img =
    await picture.toImage(100, 100); // Adjust the size here if necessary
    final byteData = await img.toByteData(format: ui.ImageByteFormat.png);
    final uint8List = byteData!.buffer.asUint8List();

    return BitmapDescriptor.fromBytes(uint8List);
  }

  @override
  Widget build(BuildContext context) {

    return Scaffold(
      body: Stack(
        children: [
          GoogleMap(
            onMapCreated: (GoogleMapController controller) {
              _controller = controller;
              _getAllData();
            },
            markers: _markers,
            polylines: _polylines,
            mapType: MapType.hybrid,
            initialCameraPosition: CameraPosition(
              target: LatLng(34.0522, -118.2437),
              // Default location
              zoom: 8,
            ),
          ),
          Positioned(
            bottom: 20,
            left: 20,
            child: FloatingActionButton(
              onPressed: () async {
                LatLngBounds visibleRegion =
                await _controller.getVisibleRegion();
                LatLng center = LatLng(
                  (visibleRegion.northeast.latitude +
                      visibleRegion.southwest.latitude) /
                      2,
                  (visibleRegion.northeast.longitude +
                      visibleRegion.southwest.longitude) /
                      2,
                );
                _addMarkerWithAnimation(center);
              },
              child: Icon(Icons.add),
            ),
          ),
        ],
      ),
    );
  }

  Future<void> processWaivesArray(List<dynamic> data) async {
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!");
    print(data);
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!");


    for (var coord in data) {
      LatLng position = LatLng(coord['latitude'], coord['longitude']);
      _addMarkerWithoutAnimation(position, coord['id']);
    }


    ApiService apiService = ApiService(); // No parameters needed!

    String userRole = await apiService.getUserRole();

    List<LatLng> trajectory = await apiService.getTrajectoryData();
    coordinates = trajectory;
    addTrajectory(trajectory);

    LatLng currentCoord = await apiService.getCurrentIssCoordinates();
    _setIssMarker(currentCoord);
    _startMarkerMovement();
  }

  Timer? _timer;
  int _currentIndex = 0;

  Future<void> _moveMarker(LatLng position) async {
    final Marker marker = await _createMarker(position, 'iss');

    setState(() {
      _markers.add(
          marker); // Update the set of markers to include only the moving marker
    });
  }

  @override
  void dispose() {
    _timer?.cancel(); // Cancel the timer when the widget is disposed
    super.dispose();
  }

  void _startMarkerMovement() {
    // Create a periodic timer that updates the marker's position
    _timer = Timer.periodic(Duration(seconds: 1), (Timer timer) {
      if (_currentIndex < coordinates.length - 1) {
        _currentIndex++;
        _moveMarker(coordinates[
        _currentIndex]); // Move the marker to the next coordinate
      } else {
        // Stop the timer if we reach the end of the route
        _timer?.cancel();
      }
    });
  }

  void addTrajectory(List<LatLng> coordinates) {
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!");
    //print(data);
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!");
    final PolylineId polylineId = PolylineId("dynamic_route");

    // Create a new polyline with the passed coordinates
    final Polyline polyline = Polyline(
      polylineId: polylineId,
      color: Colors.blue,
      width: 4,
      points: coordinates,
    );

    setState(() {
      _polylines.add(polyline); // Update the set of polylines
    });
  }

  Future<void> _getAllData() async {
    ApiService apiService = ApiService();
    List? waives = await apiService.fetchData();
    print("**************************************");
    print(waives);
    print("**************************************");
    processWaivesArray(waives);
  }
}
