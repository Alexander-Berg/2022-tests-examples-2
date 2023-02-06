import 'package:hooks_riverpod/hooks_riverpod.dart';

import 'app_state.dart';

class AppStateHolder extends StateNotifier<AppState> {
  AppStateHolder([AppState? state]) : super(state ?? const AppState());

  void setState(AppState appState) => state = appState;

  void setTheme(AppStateTheme theme) {
    state = state.copyWith(theme: theme);
  }

  void setDarkTheme() => setTheme(AppStateTheme.dark);
  void setLightTheme() => setTheme(AppStateTheme.light);
}
