import 'package:freezed_annotation/freezed_annotation.dart';

part 'state.freezed.dart';

@freezed
class PaymentPageState with _$PaymentPageState {
  factory PaymentPageState({
    @Default(PaymentOption.cash) PaymentOption selected,
    @Default(false) bool isLoading,
    @Default([PaymentOption.cash]) List<PaymentOption> enabledOptions,
  }) = _PaymentPageState;
}

enum PaymentOption {
  card,
  cash,
  none,
}
