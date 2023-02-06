import '../../../api/shop_api.dart';
import 'shop_state_holder.dart';

class ShopManager {
  final ShopApi shopApi;
  final ShopStateHolder shopStateHolder;

  ShopManager({
    required this.shopApi,
    required this.shopStateHolder,
  });

  void onInit() {
    loadCategories();
  }

  Future<void> loadCategories() async {
    final categories = await shopApi.getCategories();
    shopStateHolder.setCategories(categories);
  }
}
