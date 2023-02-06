import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:models/models.dart';

import '../../../../profile/domain/profile_page_state.dart';
import 'shop_state.dart';

class ShopStateHolder extends StateNotifier<ShopState> {
  ShopStateHolder([ShopState? initial]) : super(initial ?? const ShopState());

  void setCategories(List<Category> categories) {
    state = state.copyWith(categories: categories, status: ProgressState.done);
  }
}
