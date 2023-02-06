import 'package:models/models.dart';

import '../../common/api/api_client.dart';
import '../../common/api/providers.dart';

class ShopApi {
  final ApiClient _apiClient;
  ShopApi(this._apiClient);

  Future<List<Category>> getCategories() async {
    final response = await _apiClient.dio.get<List>(ApiShopUrls.categories);
    final json = response.data;
    if (json == null) {
      return <Category>[];
    }

    return json
        //ignore: implicit_dynamic_parameter
        .map((c) => Category.fromJson(c as Map<String, dynamic>))
        .toList();
  }
}
