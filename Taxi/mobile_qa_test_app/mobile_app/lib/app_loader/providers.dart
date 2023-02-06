import 'package:hooks_riverpod/hooks_riverpod.dart';

import '../auth/domain/user_state_holder.dart';
import '../auth/providers.dart';
import '../build/providers.dart';
import '../common/local_storage/providers.dart';
import '../configs/configs_providers.dart';
import '../utils/navigation/navigation_manager.dart';
import 'domain/app_loader_manager.dart';
import 'domain/app_loader_state_holder.dart';
import 'domain/start_page_manager.dart';

final startPageManager = Provider((ref) => StartPageManager(
      appLoaderState: ref.watch(appLoaderStateHolderProvider),
      userStateHolder: ref.watch(userStateProvider.notifier),
      navigationManager: ref.watch(navigationManagerProvider),
    ));
final appLoaderManagerProvider =
    Provider.autoDispose<AppLoaderManager>((ref) => AppLoaderManager(
          appLoaderState: ref.watch(appLoaderStateHolderProvider.notifier),
          authStorage: ref.watch(authStorageProvider),
          localStorage: ref.watch(localStorageProvider),
          startPageManager: ref.watch(startPageManager),
          userManager: ref.watch(userManagerProvider),
          buildManager: ref.watch(buildManagerProvider),
          appManager: ref.watch(appManagerProvider),
        ));
