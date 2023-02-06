import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:models/models.dart';

import '../common/api/providers.dart';
import '../common/env/env.dart';
import '../common/env/env_state_holder.dart';
import '../common/local_storage/providers.dart';
import '../common/validation/providers.dart';
import '../utils/navigation/navigation_manager.dart';
import 'api/build_api.dart';
import 'api/mock_build_api.dart';
import 'domain/manager.dart';
import 'domain/state_holder.dart';
import 'ui/build_view_model.dart';
import 'ui/domain/state.dart';
import 'ui/domain/state_holder.dart';

export 'package:qa_test_app/build/domain/state_holder.dart';

final buildManagerProvider = Provider(
  (ref) => BuildManager(
    ref.watch(buildApiProvider),
    ref.watch(buildStateHolderProvider.notifier),
    ref.watch(buildPageStateHolderProvider.notifier),
    ref.watch(navigationManagerProvider),
    ref.watch(localStorageProvider),
  ),
);

final buildApiProvider = Provider<BuildApi>(
  (ref) => ref.watch(envStateHolder).when(
        dev: MockBuildApi(),
        prod: BuildApi(
          ref.watch(apiClientProvider),
        ),
      ),
);

final buildViewModelProvider = Provider(
  (ref) => CodeViewModel(
    state: ref.watch(buildPageStateHolderProvider),
    validator: ref.watch(validationRulesProvider),
  ),
);
final buildStateHolderProvider = StateNotifierProvider<BuildStateHolder, Build>(
  (ref) => BuildStateHolder(),
);

final buildPageStateHolderProvider =
    StateNotifierProvider<BuildPageStateHolder, BuildPageState>(
  (ref) => BuildPageStateHolder(),
);

final isBrokenProvider = Provider.family<bool, String>(
  (ref, id) => ref.watch(buildStateHolderProvider).isBroken(id),
);
