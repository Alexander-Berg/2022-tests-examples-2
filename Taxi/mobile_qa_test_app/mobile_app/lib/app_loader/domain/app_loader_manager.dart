// import 'package:qa_test_app/auth/domain/user_manager.dart';

import '../../auth/api/auth_storage.dart';
import '../../auth/domain/local_user_manager.dart';
import '../../build/domain/manager.dart';
import '../../common/local_storage/local_storage.dart';
import '../../utils/app_manager.dart';
import 'app_loader_state_holder.dart';
import 'start_page_manager.dart';

class AppLoaderManager {
  final LocalStorage _localStorage;
  final AppLoaderStateHolder _appLoaderState;
  final AuthStorage _authStorage;
  final LocalUserManager _userManager;
  final StartPageManager _startPageManager;
  final BuildManager _buildManager;
  final AppManager _appManager;

  AppLoaderManager({
    required LocalStorage localStorage,
    required AppLoaderStateHolder appLoaderState,
    required AuthStorage authStorage,
    required LocalUserManager userManager,
    required StartPageManager startPageManager,
    required BuildManager buildManager,
    required AppManager appManager,
  })  : _localStorage = localStorage,
        _appLoaderState = appLoaderState,
        _authStorage = authStorage,
        _startPageManager = startPageManager,
        _userManager = userManager,
        _buildManager = buildManager,
        _appManager = appManager;

  Future<void> _setUp() async {
    await _appManager.init();
    await _authStorage.init();
    await _userManager.init();
    await _buildManager.init();
  }

  Future<void> onInit() async {
    try {
      await _localStorage.open();
      await _setUp();
      _appLoaderState
        ..setUp()
        ..completeSettingUp();
      _startPageManager.defineStartPage();
    } on Exception catch (e) {
      _appLoaderState.completeWithFailure(e);
    }
  }

  void onRetrySetUp() {
    onInit();
  }
}
