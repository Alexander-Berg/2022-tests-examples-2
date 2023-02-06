import '../../auth/domain/user_state_holder.dart';
import '../../utils/navigation/navigation_manager.dart';
import '../models/app_loader.dart';

class StartPageManager {
  final AppLoader appLoaderState;
  final UserStateHolder userStateHolder;
  final NavigationManager navigationManager;
  StartPageManager({
    required this.appLoaderState,
    required this.userStateHolder,
    required this.navigationManager,
  });

  void defineStartPage() {
    if (userStateHolder.user == null) {
      navigationManager.openBuildPage();
    } else {
      navigationManager.popAllAndOpenShopPage();
    }
  }
}
