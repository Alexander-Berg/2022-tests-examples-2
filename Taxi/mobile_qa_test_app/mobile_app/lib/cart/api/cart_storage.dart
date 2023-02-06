import 'package:yx_persist/yx_persist.dart';

import '../../auth/models/user.dart';
import '../domain/cart_state.dart';

class CartDao extends YxDao<String, CartState> {
  @override
  String? primaryKeyOf(CartState entity) => entity.userPhone;

  @override
  CartState fromDb(Map<String, dynamic> json) => CartState.fromJson(json);

  @override
  Map<String, dynamic> toDb(CartState entity) => entity.toJson();

  Future<void> saveCartState(CartState state) async {
    if (state.userPhone == null) {
      return;
    }
    await put(state);
  }

  Future<CartState?> cartState(User user) => getByKey(user.phone);
}
