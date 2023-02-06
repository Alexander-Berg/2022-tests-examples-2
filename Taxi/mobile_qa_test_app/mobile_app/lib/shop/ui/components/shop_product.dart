import 'package:flutter/material.dart';
import 'package:flutter_txm_ui_components/components.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:models/models.dart';

import '../../../cart/domain/cart_state.dart';
import '../../../cart/providers.dart';
import '../../../common/components/txm_product_card.dart';
import '../../../utils/extensions.dart';
import '../../../utils/formatters.dart';
import '../../../utils/localization.dart';
import '../../../utils/navigation/navigation_manager.dart';

class ShopProduct extends ConsumerWidget {
  final Product product;

  const ShopProduct({
    required this.product,
    Key? key,
  }) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final cartManager = ref.watch(cartManagerProvider);
    final cartItem = ref.watch(
      cartStateHolderProvider.select((s) => s.getCartItem(product)),
    );

    return TXMProductCard(
      price: product.finalPrice.toPrice(
        currencySymbol: Strings.of(context).rubleSign,
        locale: Localizations.localeOf(context).toLanguageTag(),
        fractionDigits: 2,
      ),
      name: product.name,
      additionText: (product.count != null) ? product.amountOf(context) : null,
      imageUrl: product.imageUrl,
      hasDiscount: product.discountedPrice != null,
      inCart: cartItem != null,
      count: cartItem?.count ?? 0,
      onIncrement: () {
        cartManager.addProduct(product);
      },
      onDecrement: () {
        cartManager.removeProduct(product);
      },
      onTap: () {
        ref.read(navigationManagerProvider).openProductPage(product);
      },
      onTapCartButton: () {
        cartManager.addProduct(product);
      },
    );
  }
}
