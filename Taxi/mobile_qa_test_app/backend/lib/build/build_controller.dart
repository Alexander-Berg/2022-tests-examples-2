import 'package:conduit/conduit.dart';
import 'package:models/models.dart';

class BuildController extends ResourceController {
  @Operation.get()
  Future<Response> getBuild(@Bind.query('id') String id) async => Response.ok(
        build1.toJson(),
      );
}
