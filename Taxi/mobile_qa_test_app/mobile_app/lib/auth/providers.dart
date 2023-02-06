import 'package:hooks_riverpod/hooks_riverpod.dart';

import '../common/api/providers.dart';
import '../common/env/env.dart';
import '../common/env/env_state_holder.dart';
import '../common/local_storage/providers.dart';
import '../utils/navigation/navigation_manager.dart';
import '../utils/toaster_manager.dart';
import 'api/auth_api.dart';
import 'api/auth_storage.dart';
import 'api/mock_auth_api.dart';
import 'domain/auth_manager.dart';
import 'domain/local_user_manager.dart';
import 'domain/sign_up_state_holder.dart';
import 'domain/user_state_holder.dart';
import 'models/auth_data.dart';

final currentUserDaoProvider = Provider((ref) {
  final storage = ref.watch(localStorageProvider);

  return storage.currentUserDataDao;
});
final userManagerProvider = Provider((ref) => LocalUserManager(
      userStateHolder: ref.watch(userStateProvider.notifier),
      localStorage: ref.watch(localStorageProvider),
    ));
final signUpStateHolderProvider =
    StateNotifierProvider<SignUpStateHolder, AuthData?>(
  (ref) => SignUpStateHolder(),
);
final authManagerProvider = Provider((ref) => AuthManager(
      authApi: ref.watch(authApiProvider),
      userManager: ref.watch(userManagerProvider),
      navigationManager: ref.watch(navigationManagerProvider),
      signUpStateHolder: ref.watch(signUpStateHolderProvider.notifier),
      toasterManager: ref.watch(toasterManagerProvider),
    ));

final authApiProvider = Provider(
  (ref) => ref.watch(envStateHolder).when<AuthApi>(
        prod: AuthApi(ref.watch(apiClientProvider)),
        dev: MockAuthApi(
          ref.watch(currentUserDaoProvider),
          ref.watch(usersDaoProvider),
        ),
      ),
);

final authStorageProvider = Provider((ref) => AuthStorage(
      localStorage: ref.watch(localStorageProvider),
    ));
