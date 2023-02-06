import 'package:yx_network/yx_network.dart';

import '../../common/local_storage/local_storage.dart';

class AuthStorage extends YXInMemoryAuthStorage implements YXAuthStorage {
  final LocalStorage _localStorage;

  AuthStorage({
    required LocalStorage localStorage,
  }) : _localStorage = localStorage;

  Future<void> init() async {
    await _copyLocalToInMemory();
  }

  Future<void> _copyLocalToInMemory() async {
    final authData = await _localStorage.authDataDao.getAuthData();
    await super.updateAuthData(authData);
  }

  @override
  YXRequestOptions? get currentAuthData => super.currentAuthData;

  @override
  Future<void> updateAuthData(
    covariant YXRequestOptionsWrapper? authData,
  ) async {
    await super.updateAuthData(authData);
    await _localStorage.authDataDao.saveAuthData(authData);
  }
}

class YXRequestOptionsWrapper extends YXRequestOptions {
  const YXRequestOptionsWrapper(
    Map<String, dynamic>? headers,
    Map<String, dynamic>? queryParams,
  ) : super(headers: headers, queryParams: queryParams);

  Map<String, dynamic> toJson() => <String, dynamic>{
        'headers': headers,
        'queryParams': queryParams,
      };

  YXRequestOptionsWrapper.fromJson(Map<String, dynamic> json)
      : super(
          headers: json['headers'] as Map<String, dynamic>?,
          queryParams: json['queryParams'] as Map<String, dynamic>?,
        );
}
