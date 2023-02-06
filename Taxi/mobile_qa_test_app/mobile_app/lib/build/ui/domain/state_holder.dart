import 'package:state_notifier/state_notifier.dart';

import 'state.dart';

class BuildPageStateHolder extends StateNotifier<BuildPageState> {
  BuildPageStateHolder([BuildPageState? initial])
      : super(
          initial ?? BuildPageState(),
        );

  String get buildCode => state.buildCode;

  void loading() => state = state.copyWith(
        isProgress: true,
        errorMessage: null,
      );

  void updateCode(String code) => state = state.copyWith(
        buildCode: code,
      );

  void complete() => state = state.copyWith(
        isProgress: false,
      );

  void failure(String message) => state = state.copyWith(
        isProgress: false,
        errorMessage: message,
      );
}
