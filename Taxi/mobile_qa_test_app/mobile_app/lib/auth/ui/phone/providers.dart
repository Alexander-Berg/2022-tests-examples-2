import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../../../common/validation/providers.dart';
import '../../../utils/navigation/navigation_manager.dart';
import '../../providers.dart';

import 'domain/phone_page_state.dart';
import 'domain/phone_page_state_holder.dart';
import 'domain/phone_page_state_manager.dart';
import 'ui/phone_view_model.dart';

final phoneViewModelProvider = Provider.autoDispose(
  (ref) => PhoneViewModel(
    state: ref.watch(phonePageStateHolder),
    validator: ref.watch(validationRulesProvider),
  ),
);

final phonePageStateHolder =
    StateNotifierProvider.autoDispose<PhonePageStateHolder, PhonePageState>(
  (_) => PhonePageStateHolder(),
);
final phonePageStateManager = Provider.autoDispose(
  (ref) => PhonePageStateManager(
    pageStateHolder: ref.watch(phonePageStateHolder.notifier),
    signUpStateHolder: ref.watch(signUpStateHolderProvider.notifier),
    navigationManager: ref.watch(navigationManagerProvider),
  ),
);
