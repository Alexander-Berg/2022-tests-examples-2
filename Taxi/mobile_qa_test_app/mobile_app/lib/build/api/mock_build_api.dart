import 'package:models/models.dart';

import 'build_api.dart';

class MockBuildApi implements BuildApi {
  @override
  Future<Build> getBuild(String id) {
    if (id == '1') {
      return Future.value(build1);
    } else if (id == '2') {
      return Future.value(build2);
    }

    return Future.value(Build.noBugs);
  }
}
