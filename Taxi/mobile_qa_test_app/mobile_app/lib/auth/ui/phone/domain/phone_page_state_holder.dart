import 'package:state_notifier/state_notifier.dart';

import 'phone_page_state.dart';

class PhonePageStateHolder extends StateNotifier<PhonePageState> {
  PhonePageStateHolder([PhonePageState? initial])
      : super(initial ?? const PhonePageState(phone: ''));

  void setPhone(String phone) {
    state = state.copyWith(phone: phone);
  }

  String get phone => state.phone;
}
