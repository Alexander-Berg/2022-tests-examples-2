import '../../../domain/auth_manager.dart';
import 'code_page_state_holder.dart';

class CodePageStateManager {
  final AuthManager authManager;
  final CodePageStateHolder pageStateHolder;
  CodePageStateManager({
    required this.pageStateHolder,
    required this.authManager,
  });

  void onCodeChanged(String code) {
    pageStateHolder.setCode(code);
  }

  void onNextButtonTapped() {
    authManager.onAuthFinished();
  }
}
