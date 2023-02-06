import '../../auth/domain/auth_manager.dart';
import '../../auth/domain/local_user_manager.dart';
import '../../cart/domain/cart_manager.dart';
import '../../utils/dialogs_manager.dart';
import '../../utils/toaster_manager.dart';
import '../domain/profile_page_manager.dart';
import '../domain/profile_page_state_holder.dart';

class BrokenProfilePageStateManager extends ProfilePageManager {
  BrokenProfilePageStateManager({
    required LocalUserManager userManager,
    required ProfilePageStateHolder pageStateHolder,
    required ToasterManager toasterManager,
    required AuthManager authManager,
    required DialogsManager dialogsManager,
    required CartManager cartManager,
  }) : super(
          userManager: userManager,
          pageStateHolder: pageStateHolder,
          toasterManager: toasterManager,
          authManager: authManager,
          dialogsManager: dialogsManager,
          cartManager: cartManager,
        );

  @override
  Future<void> onSaveChangesTapped() async {
    // Nothing
  }
}
