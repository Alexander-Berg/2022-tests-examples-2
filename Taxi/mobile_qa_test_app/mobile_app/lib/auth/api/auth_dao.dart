import 'package:yx_persist/yx_persist.dart';

import '../../common/local_storage/local_storage.dart';
import 'auth_storage.dart';

class AuthDao extends YxDao<String, YXRequestOptionsWrapper> {
  @override
  String primaryKeyOf(YXRequestOptionsWrapper entity) => StorageKeys.authData;

  @override
  YXRequestOptionsWrapper fromDb(Map<String, dynamic> json) =>
      YXRequestOptionsWrapper.fromJson(json);

  Future<YXRequestOptionsWrapper> getAuthData() async =>
      getByKey(StorageKeys.authData);

  Future<void> saveAuthData(YXRequestOptionsWrapper? data) async => put(data);

  @override
  Map<String, dynamic> toDb(YXRequestOptionsWrapper entity) => entity.toJson();
}
