import '../../../../utils/navigation/navigation_manager.dart';

import '../../../domain/sign_up_state_holder.dart';
import 'phone_page_state_holder.dart';

class PhonePageStateManager {
  final PhonePageStateHolder pageStateHolder;
  final SignUpStateHolder signUpStateHolder;
  final NavigationManager navigationManager;
  PhonePageStateManager({
    required this.pageStateHolder,
    required this.signUpStateHolder,
    required this.navigationManager,
  });

  void onPhoneChanged(String phone) {
    pageStateHolder.setPhone(phone);
  }

  void onNextsButtonTapped() {
    signUpStateHolder.setPhone(pageStateHolder.phone);
    navigationManager.openCodePage();
  }
}
