import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:models/models.dart';

import '../build/providers.dart';
import '../common/local_storage/providers.dart';
import '../common/validation/models/validation_rules.dart';
import '../common/validation/providers.dart';
import '../utils/navigation/navigation_manager.dart';
import '../utils/toaster_manager.dart';
import 'domain/manager.dart';
import 'domain/state_holder.dart';
import 'ui/domain/page_manager.dart';
import 'ui/domain/state.dart';
import 'ui/domain/state_holder.dart';

final cardPageManagerProvider = Provider.autoDispose(
  (ref) => CardPageManager(
    cardManager: ref.watch(cardManagerProvider),
    cardState: ref.watch(cardStateHolderProvider.notifier),
    navigationManager: ref.watch(navigationManagerProvider),
    state: ref.watch(cardPageStateHolderProvider.notifier),
    toasterManager: ref.watch(toasterManagerProvider),
  ),
);

final cardPageStateHolderProvider =
    StateNotifierProvider.autoDispose<CardPageStateHolder, CardPageState>(
  (ref) => CardPageStateHolder(ref.watch(validationRulesProvider)),
);

final cardPageStateProvider = Provider.autoDispose(
  (ref) => CardPageState(),
);

final cardManagerProvider = Provider(
  (ref) => CardManager(
    cardDao: ref.watch(cardDaoProvider),
    state: ref.watch(cardStateHolderProvider.notifier),
    toasterManager: ref.watch(toasterManagerProvider),
  ),
);

final cardStateHolderProvider = StateNotifierProvider(
  (ref) => CardStateHolder(),
);

final cardDaoProvider = Provider(
  (ref) => ref.watch(localStorageProvider).cardDataDao,
);

final cvvInputMaxLengthProvider = Provider<int>((ref) {
  final isBroken = ref.watch(isBrokenProvider(
    BugIds.cardCvvInputLength4,
  ));

  return isBroken
      ? BrokenValidationRules.kCvvInputLength
      : RightValidationRules.kCvvInputLength;
});
