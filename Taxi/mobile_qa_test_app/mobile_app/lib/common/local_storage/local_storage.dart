import 'dart:developer';

import 'package:yx_persist/yx_persist.dart';

import '../../auth/api/auth_dao.dart';
import '../../auth/api/current_user_dao.dart';
import '../../build/api/dao.dart';
import '../../card/api/card_storage.dart';
import '../../cart/api/cart_storage.dart';
import '../../configs/dao/app_configs_dao.dart';
import '../api/users_dao.dart';

class StorageKeys {
  static const authData = 'authData';
  static const cartData = 'cartData';
  static const cardData = 'cardData';
  static const userData = 'userData';
  static const buildData = 'buildData';
  static const appData = 'appData';
}

class LocalStorage extends YxPersist {
  @override
  String get name => 'qa_test_app.db';

  @override
  Future<void> onVersionChanged(int oldVersion, int newVersion) async =>
      log('migrating from $oldVersion to $newVersion');

  AuthDao get authDataDao => dao(StorageKeys.authData, () => AuthDao());
  CartDao get cartDataDao => dao(StorageKeys.cartData, () => CartDao());
  CardDao get cardDataDao => dao(StorageKeys.cardData, () => CardDao());
  BuildDao get buildDataDao => dao(StorageKeys.buildData, () => BuildDao());
  CurrentUserDao get currentUserDataDao =>
      dao(StorageKeys.userData, () => CurrentUserDao());
  UsersDao get usersDataDao => dao('users', () => UsersDao());
  AppConfigsDao get appConfigsDao =>
      dao(StorageKeys.appData, () => AppConfigsDao());

  @override
  int get version => 4;
}
