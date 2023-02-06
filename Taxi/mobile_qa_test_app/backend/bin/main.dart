import 'package:qa_test_server/qa_test_server.dart';

Future main() async {
  final app = Application<QaTestServerChannel>()
    ..options.configurationFilePath = "config.yaml";

  await app.startOnCurrentIsolate();

  print("Application started on port: ${app.options.port}.");
  print("Use Ctrl-C (SIGINT) to stop running the application.");
}
