import 'package:state_notifier/state_notifier.dart';

import '../models/auth_data.dart';

class SignUpStateHolder extends StateNotifier<AuthData?> {
  SignUpStateHolder([AuthData? initial]) : super(initial);

  void setState(AuthData authUser) => state = authUser;

  void setName(String name) {
    final user = state;
    if (user != null && user is AuthDataSignUp) {
      state = user.copyWith(name: name);
    }
  }

  void setFio(String name, String surname, String patronymic) {
    setName(name);
    setSurname(surname);
    setPatronymic(patronymic);
  }

  void setSurname(String surname) {
    final user = state;
    if (user is AuthDataSignUp) {
      state = user.copyWith(surname: surname);
    }
  }

  void setPatronymic(String patronymic) {
    final user = state;
    if (user is AuthDataSignUp) {
      state = user.copyWith(patronymic: patronymic);
    }
  }

  void setPhone(String phone) {
    final user = state;
    if (user != null) {
      user.map(
        signIn: (signIn) => state = signIn.copyWith(phone: phone),
        signUp: (signUp) => state = signUp.copyWith(phone: phone),
      );
    }
  }
}
