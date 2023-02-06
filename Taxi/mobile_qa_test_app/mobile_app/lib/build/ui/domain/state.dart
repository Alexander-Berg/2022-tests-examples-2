import 'package:freezed_annotation/freezed_annotation.dart';

part 'state.freezed.dart';

@freezed
class BuildPageState with _$BuildPageState {
  factory BuildPageState({
    @Default(false) bool isProgress,
    @Default(null) String? errorMessage,
    @Default('') String buildCode,
  }) = _BuildPageState;
}
