import '../../card/domain/manager.dart';
import '../../card/domain/state_holder.dart';
import '../../cart/domain/cart_manager.dart';
import '../../utils/navigation/navigation_manager.dart';
import 'state.dart';
import 'state_holder.dart';

class PaymentPageManager {
  final PaymentPageStateHolder pageState;
  final CardManager cardManager;
  final CardStateHolder cardState;
  final NavigationManager navigationManager;
  final CartManager cartManager;

  PaymentPageManager({
    required this.pageState,
    required this.cardManager,
    required this.cardState,
    required this.navigationManager,
    required this.cartManager,
  });

  Future<void> onInit() async {
    pageState.loading();
    await cardManager.init();
    if (cardState.getCard() != null) {
      pageState.addCardPaymentOption();
    }
    pageState.completeLoading();
  }

  void pay() {
    cartManager.clear();
    navigationManager.openPaymentResultPage();
  }

  void onChoosePaymentOption(PaymentOption option) {
    pageState.choosePaymentOption(option);
  }
}
