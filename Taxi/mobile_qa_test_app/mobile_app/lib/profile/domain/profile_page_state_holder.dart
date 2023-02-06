import 'package:state_notifier/state_notifier.dart';

import '../../auth/models/user.dart';
import 'profile_page_state.dart';

class ProfilePageStateHolder extends StateNotifier<ProfilePageState> {
  ProfilePageStateHolder([ProfilePageState? initialState])
      : super(initialState ?? const ProfilePageState());

  void onInit(User user) {
    state = state.copyWith(
      name: user.name,
      surname: user.surname,
      patronymic: user.patronymic ?? '',
      phone: user.phone,
    );
  }

  void setLoadingState(ProgressState loadingState) {
    state = state.copyWith(loadingState: loadingState);
  }

  void setName(String name) {
    state = state.copyWith(name: name);
  }

  void setSurname(String surname) {
    state = state.copyWith(surname: surname);
  }

  void setPatronymic(String patronymic) {
    state = state.copyWith(patronymic: patronymic);
  }

  void setPhone(String phone) {
    state = state.copyWith(phone: phone);
  }

  void setSavingState(ProgressState savingState) {
    state = state.copyWith(savingState: savingState);
  }
}
