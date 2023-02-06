import '../../card/domain/manager.dart';
import '../../card/domain/state_holder.dart';
import '../../cart/domain/cart_manager.dart';
import '../../utils/navigation/navigation_manager.dart';
import '../domain/page_manager.dart';
import '../domain/state.dart';
import '../domain/state_holder.dart';
import 'state_holder.dart';

class BrokenPaymentPageManager extends PaymentPageManager {
  final PaymentPageBrokenStateHolder _brokenState;
  BrokenPaymentPageManager(
    PaymentPageStateHolder state,
    CardManager cardManager,
    CardStateHolder cardState,
    NavigationManager navigationManager,
    CartManager cartManager,
    this._brokenState,
  ) : super(
          pageState: state,
          cardManager: cardManager,
          cardState: cardState,
          navigationManager: navigationManager,
          cartManager: cartManager,
        );

  @override
  void onChoosePaymentOption(PaymentOption option) => _brokenState.freeze();
}
