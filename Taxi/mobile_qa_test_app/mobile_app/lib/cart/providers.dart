import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:models/models.dart';

import '../auth/domain/user_state_holder.dart';
import '../build/providers.dart';
import '../common/local_storage/providers.dart';
import '../utils/navigation/navigation_manager.dart';
import '../utils/toaster_manager.dart';
import 'broken/broken_cart_manager.dart';
import 'domain/cart_manager.dart';
import 'domain/cart_state.dart';
import 'domain/cart_state_holder.dart';

final cartDaoProvider = Provider(
  (ref) => ref.watch(localStorageProvider).cartDataDao,
);
final cartStateHolderProvider =
    StateNotifierProvider<CartStateHolder, CartState>(
  (ref) {
    final user = ref.watch(userStateProvider);

    return CartStateHolder(CartState([], user?.phone));
  },
);

final cartManagerProvider = Provider<CartManager>(
  (ref) {
    final isIncrementBroken = ref.watch(isBrokenProvider(
      BugIds.shopProductOnIncrementDouble,
    ));
    final isDecrementBroken = ref.watch(isBrokenProvider(
      BugIds.shopProductOnDecrementInverse,
    ));
    final isClearBroken = ref.watch(isBrokenProvider(
      BugIds.cartClearDoesNotWork,
    ));

    if (isIncrementBroken || isClearBroken || isDecrementBroken) {
      return BrokenCartManager(
        ref.watch(localStorageProvider).cartDataDao,
        ref.watch(cartStateHolderProvider.notifier),
        ref.watch(userStateProvider),
        ref.watch(navigationManagerProvider),
        ref.watch(toasterManagerProvider),
        isIncrementBroken: isIncrementBroken,
        isDecrementBroken: isDecrementBroken,
        isClearBroken: isClearBroken,
      );
    }

    return CartManager(
      cartDao: ref.watch(localStorageProvider).cartDataDao,
      cartStateHolder: ref.watch(cartStateHolderProvider.notifier),
      currentUser: ref.watch(userStateProvider),
      navigationManager: ref.watch(navigationManagerProvider),
      toasterManager: ref.watch(toasterManagerProvider),
    );
  },
);
