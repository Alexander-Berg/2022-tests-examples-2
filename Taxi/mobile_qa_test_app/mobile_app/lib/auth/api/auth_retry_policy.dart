import 'package:yx_network/yx_network.dart';

class AuthRetryPolicy extends YXRetryPolicy {
  AuthRetryPolicy()
      : super(
          predicate: (e) => e is DioError && e.response?.statusCode == 401,
        );
}
