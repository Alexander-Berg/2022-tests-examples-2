import 'package:hooks_riverpod/hooks_riverpod.dart';

import '../auth/domain/user_state_holder.dart';
import '../auth/providers.dart';
import '../common/validation/providers.dart';
import '../utils/navigation/navigation_manager.dart';
import 'domain/address_page_manager.dart';
import 'domain/address_page_state.dart';
import 'domain/address_page_state_holder.dart';
import 'ui/address_page_view_model.dart';

final addressPageStateHolderProvider =
    StateNotifierProvider.autoDispose<AddressPageStateHolder, AddressPageState>(
  (ref) {
    final address = ref.watch(userStateProvider)?.address;

    return AddressPageStateHolder(address);
  },
);

final addressPageViewModelProvider = Provider.autoDispose(
  (ref) => AddressPageViewModel(
    pageState: ref.watch(addressPageStateHolderProvider),
    validationRules: ref.watch(validationRulesProvider),
  ),
);

final addressPageManager = Provider.autoDispose(
  (ref) => AddressPageManager(
    pageStateHolder: ref.watch(addressPageStateHolderProvider.notifier),
    userManager: ref.watch(userManagerProvider),
    navigationManager: ref.watch(navigationManagerProvider),
  ),
);
