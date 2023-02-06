import 'package:hooks_riverpod/hooks_riverpod.dart';

import '../../../common/api/providers.dart';
import 'domain/shop_manager.dart';
import 'domain/shop_state.dart';
import 'domain/shop_state_holder.dart';

final shopStateHolderProvider =
    StateNotifierProvider<ShopStateHolder, ShopState>(
  (ref) => ShopStateHolder(),
);
final shopManagerProvider = Provider((ref) => ShopManager(
      shopApi: ref.watch(shopApiProvider),
      shopStateHolder: ref.watch(shopStateHolderProvider.notifier),
    ));
