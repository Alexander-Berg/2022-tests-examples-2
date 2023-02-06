import 'package:freezed_annotation/freezed_annotation.dart';

part 'signup_page_state.freezed.dart';
// part 'phone_page_state.g.dart';

@freezed
class SignUpPageState with _$SignUpPageState {
  const factory SignUpPageState({
    @Default('') String name,
    @Default('') String surname,
    @Default('') String patronymic,
  }) = _SignUpPageState;
}
