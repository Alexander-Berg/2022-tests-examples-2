//ignore_for_file: avoid-non-null-assertion

import 'package:models/models.dart';

import '../../common/api/api_client.dart';
import '../../common/api/api_paths.dart';

class BuildApi {
  final ApiClient _client;

  BuildApi(this._client);

  Future<Build> getBuild(String id) async {
    final responce = await _client.dio.get<Map<String, dynamic>>(
      ApiPaths.build,
      queryParameters: <String, dynamic>{'id': id},
    );

    return Build.fromJson(responce.data!);
  }
}
