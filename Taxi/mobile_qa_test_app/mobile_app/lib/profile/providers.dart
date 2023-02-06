import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:models/models.dart';

import '../auth/providers.dart';
import '../build/providers.dart';
import '../cart/providers.dart';
import '../utils/dialogs_manager.dart';
import '../utils/toaster_manager.dart';
import 'broken/manager.dart';
import 'domain/profile_page_manager.dart';
import 'domain/profile_page_state.dart';
import 'domain/profile_page_state_holder.dart';

final profilePageStateHolder =
    StateNotifierProvider.autoDispose<ProfilePageStateHolder, ProfilePageState>(
  (_) => ProfilePageStateHolder(),
);
final profilePageStateManager = Provider.autoDispose(
  (ref) {
    final isBroken =
        ref.watch(isBrokenProvider(BugIds.profileOnSaveDoesNotWork));

    if (isBroken) {
      return BrokenProfilePageStateManager(
        pageStateHolder: ref.watch(profilePageStateHolder.notifier),
        userManager: ref.watch(userManagerProvider),
        toasterManager: ref.watch(toasterManagerProvider),
        authManager: ref.watch(authManagerProvider),
        dialogsManager: ref.watch(dialogsManagerProvider),
        cartManager: ref.watch(cartManagerProvider),
      );
    }

    return ProfilePageManager(
      pageStateHolder: ref.watch(profilePageStateHolder.notifier),
      userManager: ref.watch(userManagerProvider),
      toasterManager: ref.watch(toasterManagerProvider),
      authManager: ref.watch(authManagerProvider),
      dialogsManager: ref.watch(dialogsManagerProvider),
      cartManager: ref.watch(cartManagerProvider),
    );
  },
);
