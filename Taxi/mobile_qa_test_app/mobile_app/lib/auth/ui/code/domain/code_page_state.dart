import 'package:freezed_annotation/freezed_annotation.dart';

part 'code_page_state.freezed.dart';
// part 'phone_page_state.g.dart';

@freezed
class CodePageState with _$CodePageState {
  const factory CodePageState({
    @Default('') String code,
  }) = _CodePageState;
}
