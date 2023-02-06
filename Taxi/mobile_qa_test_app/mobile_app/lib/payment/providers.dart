import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:models/models.dart';

import '../build/providers.dart';
import '../card/providers.dart';
import '../cart/providers.dart';
import '../common/broken/broken_widget.dart';
import '../utils/navigation/navigation_manager.dart';
import 'broken/manager.dart';
import 'broken/state_holder.dart';
import 'domain/page_manager.dart';
import 'domain/state.dart';
import 'domain/state_holder.dart';

final paymentPageManager = Provider.autoDispose(
  (ref) {
    final isBroken = ref.watch(isBrokenProvider(
      BugIds.paymentOptionsOnTapFreezed,
    ));

    if (isBroken) {
      return BrokenPaymentPageManager(
        ref.watch(paymentPageStateHolderProvider.notifier),
        ref.watch(cardManagerProvider),
        ref.watch(cardStateHolderProvider.notifier),
        ref.watch(navigationManagerProvider),
        ref.watch(cartManagerProvider),
        ref.watch(paymentPageBrokenStateHolderProvider.notifier),
      );
    }

    return PaymentPageManager(
      pageState: ref.watch(paymentPageStateHolderProvider.notifier),
      cardManager: ref.watch(cardManagerProvider),
      cardState: ref.watch(cardStateHolderProvider.notifier),
      navigationManager: ref.watch(navigationManagerProvider),
      cartManager: ref.watch(cartManagerProvider),
    );
  },
);

final paymentPageStateHolderProvider =
    StateNotifierProvider.autoDispose<PaymentPageStateHolder, PaymentPageState>(
  (ref) => PaymentPageStateHolder(),
);

final paymentPageBrokenStateHolderProvider =
    StateNotifierProvider.autoDispose<PaymentPageBrokenStateHolder, BrokenType>(
  (ref) => PaymentPageBrokenStateHolder(),
);
