import 'package:hooks_riverpod/hooks_riverpod.dart';

import '../models/app_loader.dart';

final appLoaderStateHolderProvider =
    StateNotifierProvider<AppLoaderStateHolder, AppLoader>(
  (ref) => AppLoaderStateHolder(),
);

class AppLoaderStateHolder extends StateNotifier<AppLoader> {
  AppLoaderStateHolder([AppLoader? state])
      : super(state ?? AppLoaderInProgress());

  void completeSettingUp() {
    state = AppLoaderCompleted();
  }

  void setUp() {
    state = AppLoaderInProgress();
  }

  void completeWithFailure(Exception e) {
    state = AppLoaderFailured(e.toString());
  }
}
