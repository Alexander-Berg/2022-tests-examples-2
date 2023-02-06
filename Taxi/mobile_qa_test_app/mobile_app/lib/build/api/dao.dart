import 'package:models/models.dart';
import 'package:yx_persist/yx_persist.dart';

import '../../common/local_storage/local_storage.dart';

class BuildDao extends YxDao<String, Build> {
  @override
  String primaryKeyOf(Build build) => StorageKeys.buildData;

  Future<Build?> getBuild() async => getByKey(StorageKeys.buildData);

  Future<void> saveBuild(Build build) async => put(build);

  @override
  Build fromDb(Map<String, dynamic> json) => Build.fromJson(json);

  @override
  Map<String, dynamic> toDb(Build build) => build.toJson();
}
