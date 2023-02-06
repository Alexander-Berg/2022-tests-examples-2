import 'package:freezed_annotation/freezed_annotation.dart';

part 'phone_page_state.freezed.dart';
// part 'phone_page_state.g.dart';

@freezed
class PhonePageState with _$PhonePageState {
  const factory PhonePageState({
    required String phone,
  }) = _PhonePageState;
}
