import 'package:conduit_test/conduit_test.dart';
import 'package:qa_test_server/channel.dart';
import 'package:test/test.dart';

import 'harness.dart';

Future main() async {
  final harness = Harness()..install();

  test("GET /build/* returns 200 with body ..", () async {
    final response = await harness.agent?.get("/build/?id=10");

    expectResponse(
      response,
      200,
      body: {
        "id": "10",
        "bugs": [
          {"id": "1", "name": "code_enter_crush", "isActive": true},
          {"id": "2", "name": "cvv_4_digits", "isActive": true}
        ]
      },
    );
  });
}
