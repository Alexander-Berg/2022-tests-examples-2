import 'package:freezed_annotation/freezed_annotation.dart';

part 'app_state.freezed.dart';
part 'app_state.g.dart';

enum AppStateTheme { dark, light }

@freezed
class AppState with _$AppState {
  const factory AppState({
    @Default(AppStateTheme.light) AppStateTheme theme,
  }) = _AppState;

  factory AppState.fromJson(Map<String, dynamic> json) =>
      _$AppStateFromJson(json);
}

extension AppStateX on AppState {
  bool get isLight => theme == AppStateTheme.light;
  bool get isDark => theme == AppStateTheme.dark;
}
