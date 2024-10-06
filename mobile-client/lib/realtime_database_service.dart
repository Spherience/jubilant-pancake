import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

import 'package:firebase_database/firebase_database.dart';

class RealtimeDatabaseService {

  Future<Iterable<DataSnapshot>> fetchData(String token) async {
    final ref = FirebaseDatabase.instance.ref();
    final snapshot = await ref.child('').get();
    if (snapshot.exists) {
      print(snapshot.value);
    } else {
      print('No data available.');
    }
    final event = await ref.once(DatabaseEventType.value);
    print("################################################");
    print(snapshot.value);
    print("################################################");
    // final username = event.snapshot.value?.username ?? 'Anonymous';

    if (snapshot.value != null) {
      // If the server returns a successful response, parse the JSON
      return snapshot.children;
    } else {
      // If the server returns an error, throw an exception
      throw Exception('Failed to load data');
    }
  }
}
