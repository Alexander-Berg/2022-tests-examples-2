import 'package:freezed_annotation/freezed_annotation.dart';

part 'state.freezed.dart';

@freezed
class CardPageState with _$CardPageState {
  const factory CardPageState({
    @Default('') final String cardNumber,
    @Default('') final String validityPeriod,
    @Default('') final String cvv,
    @Default('') final String owner,
    @Default(false) final bool cardNumberInvalid,
    @Default(false) final bool validityPeriodInvalid,
    @Default(false) final bool cvvInvalid,
    @Default(false) final bool ownerInvalid,
    @Default(false) final bool isLoading,
  }) = _CardPageState;
}

extension CardPageStateValidation on CardPageState {
  bool get formIsValid =>
      formIsFilled &&
      !cardNumberInvalid &&
      !cvvInvalid &&
      !ownerInvalid &&
      !validityPeriodInvalid;

  bool get formIsFilled =>
      cardNumber.isNotEmpty &&
      cvv.isNotEmpty &&
      owner.isNotEmpty &&
      validityPeriod.isNotEmpty;
}
