import 'package:yx_persist/yx_persist.dart';

import '../../common/local_storage/local_storage.dart';

class CurrentUserDao extends YxDao<String, String> {
  @override
  String primaryKeyOf(String entity) => StorageKeys.userData;
  @override
  String fromDb(Map<String, dynamic> json) => json['phone'] as String;

  Future<String?> getCurrentUser() async => getByKey(StorageKeys.userData);

  Future<String> saveUser(String user) => put(user);

  Future<void> signOut() => removeAll();

  @override
  Map<String, dynamic> toDb(String entity) =>
      <String, dynamic>{'phone': entity};
}
