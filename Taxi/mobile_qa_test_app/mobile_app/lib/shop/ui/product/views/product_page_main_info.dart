import 'package:flutter_txm_ui_components/components.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:models/models.dart';

import '../../../../cart/domain/cart_state.dart';
import '../../../../cart/providers.dart';
import '../../../../common/components/txm_counter_button.dart';
import '../../../../common/components/txm_small_button.dart';
import '../../../../utils/extensions.dart';
import '../../../../utils/formatters.dart';
import '../../../../utils/localization.dart';
import '../../components/shop_section.dart';

class ProductPageMainInfo extends ConsumerWidget {
  final Product product;

  const ProductPageMainInfo({required this.product, Key? key})
      : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = YXTheme.of<YXThemeData>(context);
    const productImageHeight = 200.0;
    final cartItem = ref.watch(
      cartStateHolderProvider.select((s) => s.getCartItem(product)),
    );
    final cartManager = ref.watch(cartManagerProvider);

    return ShopSection(
      borderRadiusType: ShopSectionBorderRadiusType.bottom,
      child: Column(
        children: [
          TXMImageViewer(
            url: product.imageUrl,
            height: productImageHeight,
          ),
          YXListItem(
            borderType: YXListBorderType.none,
            title: product.name,
            subtitle:
                (product.count != null) ? product.amountOf(context) : null,
            subtitleColor: theme.listItemTheme.titleStyle.color,
          ),
          YXListItem(
            borderType: YXListBorderType.none,
            title: product.finalPrice.toPrice(
              currencySymbol: Strings.of(context).rubleSign,
              locale: Localizations.localeOf(context).toLanguageTag(),
              fractionDigits: 2,
            ),
            trail: (cartItem == null)
                ? TXMSmallButton(
                    isAccent: true,
                    title: Strings.of(context).addToCard,
                    onTap: () => cartManager.addProduct(product),
                  )
                : TXMCounterButton(
                    cartItem.count,
                    onDecrement: () => cartManager.removeProduct(product),
                    onIncrement: () => cartManager.addProduct(product),
                  ),
          ),
        ],
      ),
    );
  }
}
