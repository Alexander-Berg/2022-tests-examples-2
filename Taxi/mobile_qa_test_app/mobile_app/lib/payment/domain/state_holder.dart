import 'package:state_notifier/state_notifier.dart';

import 'state.dart';

class PaymentPageStateHolder extends StateNotifier<PaymentPageState> {
  PaymentPageStateHolder() : super(PaymentPageState());

  void loading() => state = state.copyWith(isLoading: true);

  void completeLoading() => state = state.copyWith(isLoading: false);

  void choosePaymentOption(PaymentOption option) =>
      state = state.copyWith(selected: option);

  void addCardPaymentOption() => state = state.copyWith(
        enabledOptions: [
          ...state.enabledOptions,
          PaymentOption.card,
        ],
      );
}
