import 'package:state_notifier/state_notifier.dart';

import 'code_page_state.dart';

class CodePageStateHolder extends StateNotifier<CodePageState> {
  CodePageStateHolder([CodePageState? initial])
      : super(initial ?? const CodePageState());

  void setCode(String code) {
    state = state.copyWith(code: code);
  }
}
