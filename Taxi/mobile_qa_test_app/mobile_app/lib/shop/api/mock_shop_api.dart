import 'dart:math';

import 'package:models/models.dart';

import '../../common/api/api_client.dart';
import 'shop_api.dart';

class MockShopApi implements ShopApi {
  @override
  final ApiClient _apiClient;
  MockShopApi(ApiClient apiClient) : _apiClient = apiClient;

  @override
  Future<List<Category>> getCategories() async {
    const exapmleProduct = Product(
      id: 'id',
      name: 'Bananas',
      imageUrl:
          'https://avatars.mds.yandex.net/get-eda/3507285/9f9eb39c9b8410734abd74076611b995/200x200nocrop',
      priceUnit: PriceUnit.rub,
      price: 10.0,
      parameters: [ProductParameter(name: 'name', value: 'd1', id: '')],
    );
    final cats = [
      Category(
        id: '1',
        title: 'Овощи и фрукты',
        imageUrl: exapmleProduct.imageUrl,
        categories: [
          Category(
            id: '1.1',
            title: 'Овощи',
            products: List.generate(
              10,
              (index) => exapmleProduct.copyWith(
                id: '${exapmleProduct.id}${Random().nextDouble() * 100}',
                price: Random().nextDouble() * 10,
                discountedPrice: Random().nextBool() ? null : 3.0,
                count: 10,
                typeCount: CountType.killograms,
              ),
            ),
          ),
          Category(
            id: '1.2',
            title: 'Фрукты',
            products: List.generate(
              10,
              (index) => exapmleProduct.copyWith(
                id: '${exapmleProduct.id}${Random().nextDouble() * 100}',
                price: Random().nextDouble() * 10,
                discountedPrice: Random().nextBool() ? null : 3.0,
                count: 10,
                typeCount: CountType.killograms,
              ),
            ),
          ),
        ],
      ),
    ];

    return cats;
  }
}
