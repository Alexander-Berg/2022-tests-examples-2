import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:models/models.dart';

import 'cart_state.dart';

class CartStateHolder extends StateNotifier<CartState> {
  CartStateHolder(CartState state) : super(state);

  void addProduct(Product product) {
    final index = state.items.indexWhere(
      (element) => element.product.id == product.id,
    );
    if (index == -1) {
      state = state.copyWith(
        items: state.items.toList()..add(CartItem(product: product, count: 1)),
      );
    } else {
      final cartItem = state.items[index];
      final newCartItem = cartItem.copyWith(count: cartItem.count + 1);
      state = state.copyWith(
        items: state.items.toList()..setAll(index, [newCartItem]),
      );
    }
  }

  void removeProduct(Product product) {
    final index = state.items.indexWhere(
      (element) => element.product.id == product.id,
    );
    if (index != -1) {
      final cartItem = state.items[index];

      if (cartItem.count == 1) {
        state = state.copyWith(
          items: state.items.toList()..removeAt(index),
        );
      } else {
        final newCartItem = cartItem.copyWith(count: cartItem.count - 1);
        state = state.copyWith(
          items: state.items.toList()..setAll(index, [newCartItem]),
        );
      }
    }
  }

  void clear() {
    state = state.copyWith(items: []);
  }

  void setCart(CartState newState) {
    state = newState;
  }

  @override
  CartState get state => super.state;
}
