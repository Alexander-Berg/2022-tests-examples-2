import 'dart:math';

import '../../common/api/users_dao.dart';

import '../models/auth_data.dart';
import '../models/user.dart';
import 'auth_api.dart';
import 'current_user_dao.dart';

class MockAuthApi implements AuthApi {
  final CurrentUserDao currentUserDao;
  final UsersDao usersDao;
  MockAuthApi(
    this.currentUserDao,
    this.usersDao,
  );

  @override
  Future<User> signIn(AuthDataSignIn data) async {
    final phone = data.phone;
    if (phone == null) {
      throw Exception('Fill field');
    }
    final result = await usersDao.getUser(phone);
    if (result == null) {
      throw Exception('User not found');
    }
    await currentUserDao.saveUser(phone);

    return result;
  }

  @override
  Future<User> signUp(AuthDataSignUp data) async {
    final name = data.name;
    final surname = data.surname;
    final patronymic = data.patronymic;
    final phone = data.phone;
    if (name == null ||
        surname == null ||
        patronymic == null ||
        phone == null) {
      throw Exception('Fill all fields');
    }
    final registeredUser = await usersDao.getUser(phone);
    if (registeredUser != null) {
      throw Exception('Пользователь уже существует');
    }

    final user = User(
      id: Random().nextInt(10000).toString(),
      name: name,
      patronymic: patronymic,
      surname: surname,
      phone: phone,
    );
    await usersDao.saveUser(user);
    await currentUserDao.saveUser(phone);

    return user;
  }

  Future<bool> isAuthorized() async =>
      (await currentUserDao.getCurrentUser()) != null;

  @override
  Future<User> auth(AuthData data) async =>
      data.map(signIn: signIn, signUp: signUp);

  @override
  Future<void> signOut() async => currentUserDao.signOut();
}
