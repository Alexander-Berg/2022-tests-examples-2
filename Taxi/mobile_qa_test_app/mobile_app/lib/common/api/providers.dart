import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:yx_network/yx_network.dart';

import '../../auth/api/auth_refresher.dart';
import '../../auth/api/auth_retry_policy.dart';
import '../../auth/providers.dart';
import '../../shop/api/mock_shop_api.dart';
import '../../shop/api/shop_api.dart';
import '../env/env.dart';
import '../env/env_state_holder.dart';
import 'api_client.dart';

class ApiShopUrls {
  ApiShopUrls._();

  static const baseUrl = 'http://qatestappserver3.vla.yp-c.yandex.net/';
  static const categories = 'categories';
}

final shopApiProvider = Provider(
  (ref) => ref.watch(envStateHolder).when(
        prod: ShopApi(
          ref.watch(apiClientProvider),
        ),
        dev: MockShopApi(
          ref.watch(apiClientProvider),
        ),
      ),
);

final apiClientProvider = Provider((ref) {
  final dio = YXDio();
  final config = YXNetwork(
    baseUrl: ApiShopUrls.baseUrl,
    authHandler: YXAuthHandler(
      AuthRefresher(dio),
      AuthRetryPolicy(),
      storage: ref.watch(authStorageProvider),
    ),
  );

  return ApiClient(dio, config);
});
