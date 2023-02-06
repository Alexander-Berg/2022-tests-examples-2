import '../../address/domain/address.dart';
import '../../common/local_storage/local_storage.dart';
import '../models/user.dart';
import 'user_state_holder.dart';

class LocalUserManager {
  final UserStateHolder userStateHolder;
  final LocalStorage localStorage;
  LocalUserManager({
    required this.userStateHolder,
    required this.localStorage,
  });

  Future<void> init() async {
    final phone = await localStorage.currentUserDataDao.getCurrentUser();
    final user =
        phone == null ? null : await localStorage.usersDataDao.getUser(phone);
    userStateHolder.setUser(user);
  }

  Future<void> setUser(User user) async {
    userStateHolder.setUser(user);
    await localStorage.currentUserDataDao.saveUser(user.phone);
  }

  Future<void> updateAddress(Address? address) async {
    final user = userStateHolder.user?.copyWith(address: address);
    if (user != null) {
      await _updateUser(user);
    }
  }

  Future<void> updateFullnameAndPhone({
    required String name,
    required String surname,
    required String phone,
    String? patronymic,
  }) async {
    final user = userStateHolder.user;
    final updatedUser = user?.copyWith(
      name: name,
      surname: surname,
      patronymic: patronymic,
      phone: phone,
    );

    if (user != null && updatedUser != null && user != updatedUser) {
      await _updateUser(updatedUser);
    }
  }

  Future<void> _updateUser(User updatedUser) async {
    final user = userStateHolder.user;

    if (user != null && user != updatedUser) {
      final usersDataDao = localStorage.usersDataDao;

      await usersDataDao.removeUser(user);
      await usersDataDao.saveUser(updatedUser);

      await setUser(updatedUser);
    }
  }

  void signOut() {
    userStateHolder.unAuthenticate();
    localStorage.currentUserDataDao.signOut();
  }

  Future<void> deleteProfile() async {
    final user = userStateHolder.user;
    if (user != null) {
      await localStorage.usersDataDao.removeUser(user);
      signOut();
    }
  }
}
