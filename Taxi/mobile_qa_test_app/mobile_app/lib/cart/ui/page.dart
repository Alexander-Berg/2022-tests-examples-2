import 'package:flutter_txm_ui_components/components.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:models/models.dart';

import '../../auth/domain/user_state_holder.dart';
import '../../shop/ui/components/shop_horizontal_list_products.dart';
import '../../shop/ui/components/shop_section.dart';
import '../../shop/ui/main/providers.dart';
import '../../utils/extensions.dart';
import '../../utils/formatters.dart';
import '../../utils/localization.dart';
import '../../utils/navigation/navigation_manager.dart';
import '../domain/cart_state.dart';
import '../providers.dart';

class CartPage extends ConsumerWidget {
  const CartPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = YXTheme.of<YXThemeData>(context);
    final categories =
        ref.watch(shopStateHolderProvider.select((s) => s.categories));
    final isEmptyCart =
        ref.watch(cartStateHolderProvider.select((s) => s.items.isEmpty));

    return TXMScaffold.list(
      background: theme.colorScheme.minorBackground,
      appBar: TXMScaffoldAppBar(
        leadingIcon: YXIconData.back,
        title: Text(Strings.of(context).cart),
        actions: [
          YXButtonIcon(
            icon: YXIconData.trash,
            onTap: () => ref.read(cartManagerProvider).clear(),
          ),
        ],
      ),
      actions: isEmptyCart ? null : const _CartPageActions(),
      children: [
        const _CartPageCartItems(),
        if (categories.isNotEmpty)
          ShopSection(
            title: Strings.of(context).maybeSomethingElse,
            child: Column(
              children: [
                ShopHorizontalListProducts(
                  categories.first.categories?.first.products ?? <Product>[],
                ),
              ],
            ),
          ),
      ],
    );
  }
}

class _CartPageCartItems extends ConsumerWidget {
  const _CartPageCartItems({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final cartItems = ref.watch(cartStateHolderProvider.select((s) => s.items));

    return ShopSection(
      borderRadiusType: ShopSectionBorderRadiusType.bottom,
      child: Column(
        children: cartItems
            .map(
              (e) => TXMEdaPickerCartItem(
                imageUrl: e.product.imageUrl,
                product: e.product.name,
                price: e.totalPrice.toPrice(
                  currencySymbol: Strings.of(context).rubleSign,
                  fractionDigits: 2,
                  locale: Localizations.localeOf(context).toLanguageTag(),
                ),
                volume: e.product.amountOf(context),
                amount: '${e.count}',
              ),
            )
            .toList(),
      ),
    );
  }
}

class _CartPageActions extends ConsumerWidget {
  const _CartPageActions({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final address = ref.watch(userStateProvider.select((s) => s?.address));
    final totalPrice = ref.watch(
      cartStateHolderProvider.select((s) => s.totalPrice),
    );
    final cartManager = ref.watch(cartManagerProvider);
    final navigationManager = ref.watch(navigationManagerProvider);

    return TXMScaffoldActions(
      isOverflow: true,
      isRounded: true,
      primary: YXButton(
        title: Strings.of(context).toBePaid,
        subtitle: totalPrice.toPrice(
          currencySymbol: Strings.of(context).rubleSign,
          fractionDigits: 2,
          locale: Localizations.localeOf(context).toLanguageTag(),
        ),
        onTap: cartManager.onNextButtonTapped,
        state: address == null ? ButtonState.disabled : ButtonState.enabled,
      ),
      upperItems: [
        YXListItem(
          borderType: YXListBorderType.none,
          lead: const Icon(YXIconData.car),
          title: Strings.of(context).selectDeliveryAddress,
          subtitle: address == null
              ? Strings.of(context).afterYouCanPayment
              : address.fullAddress,
          trail: const Icon(YXIconData.chevronsmall2),
          onTap: navigationManager.openAdressPage,
        ),
      ],
    );
  }
}
