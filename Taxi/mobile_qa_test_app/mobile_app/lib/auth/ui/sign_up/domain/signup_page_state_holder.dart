import 'package:state_notifier/state_notifier.dart';

import 'signup_page_state.dart';

class SignUpPageStateHolder extends StateNotifier<SignUpPageState> {
  SignUpPageStateHolder([SignUpPageState? initial])
      : super(initial ?? const SignUpPageState());

  void setName(String name) {
    state = state.copyWith(name: name);
  }

  void setSurname(String surname) {
    state = state.copyWith(surname: surname);
  }

  void setPatronymic(String patronymic) {
    state = state.copyWith(patronymic: patronymic);
  }

  String get name => state.name;
  String get surname => state.surname;
  String get patronymic => state.patronymic;
}
