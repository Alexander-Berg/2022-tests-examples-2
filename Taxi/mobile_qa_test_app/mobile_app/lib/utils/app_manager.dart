import '../common/local_storage/local_storage.dart';
import '../configs/app_state.dart';
import '../configs/app_state_holder.dart';

class AppManager {
  final LocalStorage _localStorage;
  final AppStateHolder _appStateHolder;

  AppManager(this._localStorage, this._appStateHolder);

  Future<void> init() async {
    final appState = await _localStorage.appConfigsDao.getState();

    _appStateHolder.setState(appState ?? const AppState());
  }

  Future<void> setDarkTheme() async {
    _appStateHolder.setDarkTheme();
    await _localStorage.appConfigsDao.saveState(_appStateHolder.state);
  }

  Future<void> setLightTheme() async {
    _appStateHolder.setLightTheme();
    await _localStorage.appConfigsDao.saveState(_appStateHolder.state);
  }
}
