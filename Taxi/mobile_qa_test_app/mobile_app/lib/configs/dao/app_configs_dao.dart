import 'package:yx_persist/yx_persist.dart';

import '../../common/local_storage/local_storage.dart';
import '../app_state.dart';

class AppConfigsDao extends YxDao<String, AppState> {
  @override
  String primaryKeyOf(AppState entity) => StorageKeys.appData;

  Future<AppState?> getState() => getByKey(StorageKeys.appData);
  Future<void> saveState(AppState entity) => put(entity);

  @override
  AppState fromDb(Map<String, dynamic> json) => AppState.fromJson(json);

  @override
  Map<String, dynamic> toDb(AppState entity) => entity.toJson();
}
