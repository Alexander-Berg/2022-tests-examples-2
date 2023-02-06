import 'package:hooks_riverpod/hooks_riverpod.dart';

import '../models/user.dart';

final userStateProvider = StateNotifierProvider<UserStateHolder, User?>(
  (ref) => UserStateHolder(),
);

class UserStateHolder extends StateNotifier<User?> {
  UserStateHolder([User? initialState]) : super(initialState);

  void setUser(User? user) => state = user;

  User? get user => state;

  void unAuthenticate() => state = null;

  bool get isAuthenticated => state != null;
}
