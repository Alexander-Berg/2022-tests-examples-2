import '../../auth/domain/auth_manager.dart';
import '../../auth/domain/local_user_manager.dart';
import '../../cart/domain/cart_manager.dart';
import '../../utils/dialogs_manager.dart';
import '../../utils/toaster_manager.dart';
import 'profile_page_state.dart';
import 'profile_page_state_holder.dart';

class ProfilePageManager {
  final CartManager cartManager;
  final LocalUserManager userManager;
  final ProfilePageStateHolder pageStateHolder;
  final ToasterManager toasterManager;
  final AuthManager authManager;
  final DialogsManager dialogsManager;

  ProfilePageManager({
    required this.cartManager,
    required this.userManager,
    required this.pageStateHolder,
    required this.toasterManager,
    required this.authManager,
    required this.dialogsManager,
  });
  void init() {
    Future.delayed(Duration.zero, () {
      final user = userManager.userStateHolder.user;
      if (user != null) {
        pageStateHolder
          ..onInit(user)
          ..setLoadingState(ProgressState.done);
      }
    });
  }

  void onNameChanged(String name) => pageStateHolder.setName(name);

  void onSurnameChanged(String surname) => pageStateHolder.setSurname(surname);

  void onPatronymicChanged(String patronymic) {
    pageStateHolder.setPatronymic(patronymic);
  }

  void onPhoneChanged(String phone) => pageStateHolder.setPhone(phone);

  Future<void> onSaveChangesTapped() async {
    try {
      pageStateHolder.setSavingState(ProgressState.loading);
      await Future.delayed(const Duration(seconds: 2), () async {
        await userManager.updateFullnameAndPhone(
          name: pageStateHolder.state.name,
          surname: pageStateHolder.state.surname,
          patronymic: pageStateHolder.state.patronymic,
          phone: pageStateHolder.state.phone,
        );
      });
      pageStateHolder.setSavingState(ProgressState.done);
      toasterManager.showSavedMessage();
    } on Exception catch (err) {
      toasterManager.showUnknowedError();
    }
  }

  Future<void> onDeleteProfileTapped() async {
    if (await dialogsManager.showConfirmDeletion()) {
      cartManager.clear();
      await userManager.deleteProfile();
      await authManager.signOut();
      toasterManager.showProfileDeletedMessage();
    }
  }
}
