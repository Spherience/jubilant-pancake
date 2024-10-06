import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:google_maps_in_flutter/api_service.dart';
import 'package:google_maps_in_flutter/realtime_database_service.dart';
import 'package:http/http.dart' as http;
import 'dart:async';
import 'package:firebase_core/firebase_core.dart';
import 'firebase_options.dart';

import 'dart:io';

import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:google_sign_in_dartio/google_sign_in_dartio.dart';

import 'auth.dart';
import 'firebase_options.dart';
import 'map_screen.dart';
import 'profile.dart';

import 'package:firebase_database/firebase_database.dart';


late final FirebaseApp app;
late final FirebaseAuth auth;
late final ApiService apiService;
FirebaseDatabase database = FirebaseDatabase.instance;

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // We're using the manual installation on non-web platforms since Google sign in plugin doesn't yet support Dart initialization.
  // See related issue: https://github.com/flutter/flutter/issues/96391

  // We store the app and auth to make testing with a named instance easier.
  app = await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  auth = FirebaseAuth.instanceFor(app: app);
  apiService = ApiService();
  apiService.initialize(app: app, auth: auth);



  // if (!kIsWeb && Platform.isWindows) {
  //   await GoogleSignInDart.register(
  //     clientId:
  //     '406099696497-g5o9l0blii9970bgmfcfv14pioj90djd.apps.googleusercontent.com',
  //   );
  // }

  //runApp(const IssTrackerApp());
  runApp(AuthExampleApp());
}

class AuthExampleApp extends StatelessWidget {
  AuthExampleApp({Key? key}) : super(key: key);

  final RealtimeDatabaseService rdbService = RealtimeDatabaseService();

  // @override
  // Widget build(BuildContext context) {
  //   return MaterialApp(
  //     title: 'Firebase Example App',
  //     theme: ThemeData(primarySwatch: Colors.amber),
  //     home: Scaffold(
  //       body: LayoutBuilder(
  //         builder: (context, constraints) {
  //           return Row(
  //             children: [
  //               Visibility(
  //                 visible: constraints.maxWidth >= 1200,
  //                 child: Expanded(
  //                   child: Container(
  //                     height: double.infinity,
  //                     color: Theme.of(context).colorScheme.primary,
  //                     child: Center(
  //                       child: Column(
  //                         mainAxisAlignment: MainAxisAlignment.center,
  //                         children: [
  //                           Text(
  //                             'Firebase Auth Desktop',
  //                             style: Theme.of(context).textTheme.headlineMedium,
  //                           ),
  //                         ],
  //                       ),
  //                     ),
  //                   ),
  //                 ),
  //               ),
  //               SizedBox(
  //                 width: constraints.maxWidth >= 1200
  //                     ? constraints.maxWidth / 2
  //                     : constraints.maxWidth,
  //                 child: StreamBuilder<User?>(
  //                   stream: auth.authStateChanges(),
  //                   builder: (context, snapshot) {
  //                     print("===================================================");
  //                     print(snapshot.hasData);
  //                     print(snapshot.data);
  //                     //print(snapshot.getIdToken())
  //                     print("===================================================");
  //                     if (snapshot.hasData) {
  //                       //app.
  //                       return const ProfilePage();
  //                     }
  //                     return const AuthGate();
  //                   },
  //                 ),
  //               ),
  //             ],
  //           );
  //         },
  //       ),
  //     ),
  //   );
  // }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Firebase Example App',
      theme: ThemeData(primarySwatch: Colors.amber),
      home: Scaffold(
        body: LayoutBuilder(
          builder: (context, constraints) {
            return Row(
              children: [
                SizedBox(
                  width: constraints.maxWidth,
                  child: StreamBuilder<User?>(
                    stream: auth.authStateChanges(),
                    builder: (context, snapshot) {
                      if (snapshot.hasData) {
                        //app.
                        //return const ProfilePage(); //we no need no profile page for now haha forget about it
                        //return MarkerZoomAnimationMap();
                        return const CustomMapScreen();
                      }
                      return const AuthGate();
                    },
                  ),
                ),
              ],
            );
          },
        ),
      ),
    );
  }
}

// class IssTrackerApp extends StatelessWidget {
//   const IssTrackerApp({Key? key}) : super(key: key);
//   @override
//   Widget build(BuildContext context) {
//     MarkerZoomAnimationMap mapScreen = MarkerZoomAnimationMap();
//     return MaterialApp(
//       title: 'ISS Tracker',
//       theme: ThemeData(
//         primarySwatch: Colors.blue,
//       ),
//       home: MarkerZoomAnimationMap(),
//     );
//   }
// }
