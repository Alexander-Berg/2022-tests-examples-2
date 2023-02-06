import 'package:conduit/conduit.dart';

class SystemController extends ResourceController {
  @Operation.get()
  Future<Response> getBuild() async => Response.ok("");
}
