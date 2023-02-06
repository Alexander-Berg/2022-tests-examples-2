import 'package:freezed_annotation/freezed_annotation.dart';

part 'address_page_state.freezed.dart';
part 'address_page_state.g.dart';

@freezed
class AddressPageState with _$AddressPageState {
  const factory AddressPageState({
    String? city,
    String? street,
    String? house,
    String? corpus,
    String? building,
  }) = _AddressPageState;

  factory AddressPageState.fromJson(Map<String, dynamic> json) =>
      _$AddressPageStateFromJson(json);
}
