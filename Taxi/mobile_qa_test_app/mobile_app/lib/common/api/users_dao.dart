import 'package:yx_persist/yx_persist.dart';

import '../../auth/models/user.dart';

class UsersDao extends YxDao<String, User> {
  @override
  String primaryKeyOf(User entity) => entity.phone;

  @override
  User fromDb(Map<String, dynamic> json) => User.fromJson(json);

  Future<User?> getUser(String phone) async => getByKey(phone);

  Future<User> saveUser(User user) => put(user);

  Future<void> removeUser(User user) => remove(user);

  @override
  Map<String, dynamic> toDb(User entity) => entity.toJson();
}
