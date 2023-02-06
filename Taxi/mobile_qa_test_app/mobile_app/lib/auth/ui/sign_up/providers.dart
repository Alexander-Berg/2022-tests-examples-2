import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../../../common/validation/providers.dart';
import '../../../utils/navigation/navigation_manager.dart';

import '../../providers.dart';
import 'domain/signup_page_state.dart';
import 'domain/signup_page_state_holder.dart';
import 'domain/signup_page_state_manager.dart';
import 'ui/sign_up_view_model.dart';

final signUpViewModelProvider = Provider.autoDispose(
  (ref) => SignUpViewModel(
    state: ref.watch(signUpPageStateHolderProvider),
    validator: ref.watch(validationRulesProvider),
  ),
);
final signUpPageStateHolderProvider =
    StateNotifierProvider.autoDispose<SignUpPageStateHolder, SignUpPageState>(
  (_) => SignUpPageStateHolder(),
);
final signUpPageStateManager = Provider.autoDispose(
  (ref) => SignUpPageStateManager(
    signUpStateHolder: ref.watch(signUpStateHolderProvider.notifier),
    pageStateHolder: ref.watch(signUpPageStateHolderProvider.notifier),
    navigationManager: ref.watch(navigationManagerProvider),
  ),
);
