import 'package:freezed_annotation/freezed_annotation.dart';

part 'profile_page_state.freezed.dart';

enum ProgressState { none, loading, error, done }

@freezed
class ProfilePageState with _$ProfilePageState {
  const factory ProfilePageState({
    @Default('') String name,
    @Default('') String surname,
    @Default('') String patronymic,
    @Default('') String phone,
    @Default(ProgressState.loading) ProgressState loadingState,
    @Default(ProgressState.done) ProgressState savingState,
  }) = _ProfilePageState;
}
