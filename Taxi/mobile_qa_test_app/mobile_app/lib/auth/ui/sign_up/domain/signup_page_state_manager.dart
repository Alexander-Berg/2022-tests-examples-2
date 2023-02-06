import '../../../../utils/navigation/navigation_manager.dart';

import '../../../domain/sign_up_state_holder.dart';
import 'signup_page_state_holder.dart';

class SignUpPageStateManager {
  final NavigationManager navigationManager;
  final SignUpStateHolder signUpStateHolder;
  final SignUpPageStateHolder pageStateHolder;
  SignUpPageStateManager({
    required this.navigationManager,
    required this.pageStateHolder,
    required this.signUpStateHolder,
  });

  void onNameChanged(String name) {
    pageStateHolder.setName(name);
  }

  void onSurnameChanged(String surname) {
    pageStateHolder.setSurname(surname);
  }

  void onPatronymicChanged(String patronymic) {
    pageStateHolder.setPatronymic(patronymic);
  }

  void onNextButtonTapped() {
    signUpStateHolder.setFio(
      pageStateHolder.name,
      pageStateHolder.surname,
      pageStateHolder.patronymic,
    );
    navigationManager.openPhonePage();
  }
}
