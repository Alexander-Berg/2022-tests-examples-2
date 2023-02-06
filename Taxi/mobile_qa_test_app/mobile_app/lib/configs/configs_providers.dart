import 'package:hooks_riverpod/hooks_riverpod.dart';

import '../common/local_storage/providers.dart';
import '../utils/app_manager.dart';
import 'app_state.dart';
import 'app_state_holder.dart';

final appStateProvider =
    StateNotifierProvider<AppStateHolder, AppState>((ref) => AppStateHolder());

final appManagerProvider = Provider((ref) => AppManager(
      ref.watch(localStorageProvider),
      ref.watch(appStateProvider.notifier),
    ));
