import 'package:yx_network/yx_network.dart';

import '../../common/api/api_paths.dart';

class AuthRefresher extends YXAuthRefresher {
  Dio dio;

  AuthRefresher(this.dio);
  @override
  Future<YXRequestOptions> fetch(YXRequestOptions? oldAuthData) async {
    final response = await dio.post<Map<String, dynamic>>(
      ApiPaths.refreshToken,
      data: {'token': oldAuthData?.headers?['auth_token'].toString()},
    );

    return YXRequestOptions(
      headers: response.headers.map,
      queryParams: response.requestOptions.queryParameters,
    );
  }
}
