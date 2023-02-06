import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:models/models.dart';

part 'cart_state.freezed.dart';
part 'cart_state.g.dart';

@freezed
class CartState with _$CartState {
  const factory CartState(List<CartItem> items, [String? userPhone]) =
      _CartState;
  const CartState._();

  factory CartState.fromJson(Map<String, dynamic> json) =>
      _$CartStateFromJson(json);
}

extension AdditionCartState on CartState {
  double get totalPrice {
    if (items.isEmpty) {
      return 0;
    }

    final totalPrices = items.map(
      (e) => e.totalPrice,
    );

    return totalPrices.reduce(
      (value, price) => value + price,
    );
  }

  CartItem? getCartItem(Product product) => items.firstWhereOrNull(
        (element) => element.product.id == product.id,
      );
}

@freezed
class CartItem with _$CartItem {
  const factory CartItem({
    required Product product,
    @Default(1) int count,
  }) = _CartItem;
  const CartItem._();

  factory CartItem.fromJson(Map<String, dynamic> json) =>
      _$CartItemFromJson(json);
}

extension AdditionCartItem on CartItem {
  double get totalPrice => product.finalPrice * count;
}

extension AdditionProduct on Product {
  double get finalPrice => discountedPrice ?? price;
}
