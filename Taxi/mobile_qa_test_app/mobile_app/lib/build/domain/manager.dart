import '../../common/local_storage/local_storage.dart';

import '../../utils/navigation/navigation_manager.dart';
import '../api/build_api.dart';
import '../ui/domain/state_holder.dart';
import 'state_holder.dart';

class BuildManager {
  final BuildApi _api;
  final BuildStateHolder _state;
  final NavigationManager _navigationManager;
  final BuildPageStateHolder _pageState;
  final LocalStorage _localStorage;

  BuildManager(
    this._api,
    this._state,
    this._pageState,
    this._navigationManager,
    this._localStorage,
  );

  Future<void> init() async {
    try {
      final build = await _localStorage.buildDataDao.getBuild();
      _state.setBuild(build);
    } on Exception catch (e) {
      // Nothing
    }
  }

  Future<void> onEnter() async {
    _pageState.loading();
    try {
      final build = await _api.getBuild(_pageState.buildCode);
      await _localStorage.buildDataDao.saveBuild(build);
      _state.setBuild(build);
      _pageState.complete();
      _navigationManager.openAuthPage();
    } on Exception catch (e) {
      _pageState.failure(e.toString());
    }
  }

  void onBuildCodeChanged(String code) {
    _pageState.updateCode(code);
  }
}
