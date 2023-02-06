import '../../utils/navigation/navigation_manager.dart';
import '../../utils/toaster_manager.dart';
import '../api/auth_api.dart';
import '../models/auth_data.dart';
import 'local_user_manager.dart';
import 'sign_up_state_holder.dart';

class AuthManager {
  final NavigationManager _navigationManager;
  final AuthApi _authApi;
  final LocalUserManager _userManager;
  final SignUpStateHolder _signUpStateHolder;
  final ToasterManager _toasterManager;

  AuthManager({
    required AuthApi authApi,
    required LocalUserManager userManager,
    required NavigationManager navigationManager,
    required SignUpStateHolder signUpStateHolder,
    required ToasterManager toasterManager,
  })  : _authApi = authApi,
        _userManager = userManager,
        _navigationManager = navigationManager,
        _signUpStateHolder = signUpStateHolder,
        _toasterManager = toasterManager;

  Future<void> signIn(AuthDataSignIn data) async {
    try {
      final user = await _authApi.signIn(data);
      await _userManager.setUser(user);
      _navigationManager.popAllAndOpenShopPage();
    } on Exception catch (e) {
      _toasterManager.showErrorUserNotFound();
    }
  }

  Future<void> onSignInClicked() async {
    _signUpStateHolder.setState(const AuthDataSignIn());
    _navigationManager.openPhonePage();
  }

  Future<void> signUp(AuthDataSignUp data) async {
    try {
      final user = await _authApi.signUp(data);
      await _userManager.setUser(user);
      _navigationManager.popAllAndOpenShopPage();
    } on Exception catch (e) {
      _toasterManager.showErrorMessage(e.toString());
    }
  }

  Future<void> onSignUpClicked() async {
    _signUpStateHolder.setState(const AuthDataSignUp());
    _navigationManager.openSignUpPage();
  }

  void onAuthFinished() {
    final state = _signUpStateHolder.state;
    if (state != null) {
      state.map(
        signIn: signIn,
        signUp: signUp,
      );
    }
  }

  Future<void> signOut() async {
    await _authApi.signOut();
    _userManager.signOut();
    _navigationManager.popAllAndOpenBuildPage();
  }

  Future<void> onSignOutClicked() async {
    try {
      await signOut();
    } on Exception catch (e) {
      _toasterManager.showErrorMessage(e.toString());
    }
  }
}
