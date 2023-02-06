import 'package:hooks_riverpod/hooks_riverpod.dart';

import '../../../common/validation/providers.dart';
import '../../providers.dart';
import 'domain/code_page_state.dart';
import 'domain/code_page_state_holder.dart';
import 'domain/code_page_state_manager.dart';
import 'ui/code_view_model.dart';

final codeViewModelProvider = Provider.autoDispose(
  (ref) => CodeViewModel(
    state: ref.watch(codePageStateHolder),
    validator: ref.watch(validationRulesProvider),
  ),
);

final codePageStateHolder =
    StateNotifierProvider.autoDispose<CodePageStateHolder, CodePageState>(
  (_) => CodePageStateHolder(),
);
final codePageStateManager = Provider.autoDispose(
  (ref) => CodePageStateManager(
    authManager: ref.watch(authManagerProvider),
    pageStateHolder: ref.watch(codePageStateHolder.notifier),
  ),
);
