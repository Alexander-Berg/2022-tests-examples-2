// ignore_for_file: cascade_invocations

import 'build/build_controller.dart';
import 'categories/categories_controller.dart';
import 'system/system_controller.dart';
import 'package:conduit/conduit.dart';

import 'build/build_controller.dart';
import 'utils/routes.dart';

class QaTestServerChannel extends ApplicationChannel {
  @override
  Future prepare() async {
    logger.onRecord.listen(
        (rec) => print("$rec ${rec.error ?? ""} ${rec.stackTrace ?? ""}"));
  }

  @override
  Controller get entryPoint {
    final router = Router();

    router
      ..route(Routes.build).link(() => BuildController())
      ..route(Routes.categories).link(() => CategoriesController())
      ..route(Routes.ping).link(() => SystemController());

    return router;
  }
}
