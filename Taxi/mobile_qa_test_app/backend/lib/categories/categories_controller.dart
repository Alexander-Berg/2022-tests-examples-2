import 'package:conduit/conduit.dart';
import 'mock_data.dart';

class CategoriesController extends ResourceController {
  @Operation.get()
  Future<Response> getBuild() async => Response.ok(categories);
}
