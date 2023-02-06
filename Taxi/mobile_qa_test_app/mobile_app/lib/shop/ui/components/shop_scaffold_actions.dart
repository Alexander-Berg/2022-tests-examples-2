import 'package:flutter_txm_ui_components/components.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

import '../../../cart/domain/cart_state.dart';
import '../../../cart/providers.dart';
import '../../../utils/formatters.dart';
import '../../../utils/localization.dart';
import '../../../utils/navigation/navigation_manager.dart';

/// По умолчанию в [actions] находится кнопка "Корзина"
class ShopScaffoldActions extends ConsumerWidget {
  final List<Widget>? upperItems;
  final Widget? primaryButton;

  const ShopScaffoldActions({
    this.upperItems,
    this.primaryButton,
    Key? key,
  }) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) => TXMScaffoldActions(
        isOverflow: true,
        isRounded: true,
        upperItems: upperItems,
        primary: primaryButton ?? const _DefaultScaffoldAction(),
      );
}

class _DefaultScaffoldAction extends HookConsumerWidget {
  const _DefaultScaffoldAction({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final navigator = ref.read(navigationManagerProvider);
    final cartState = ref.watch(cartStateHolderProvider);
    final totalPrice = cartState.totalPrice;

    return (cartState.items.isNotEmpty)
        ? YXButton(
            title: Strings.of(context).cart,
            subtitle: totalPrice.toPrice(
              currencySymbol: Strings.of(context).rubleSign,
              fractionDigits: 2,
              locale: Localizations.localeOf(context).toLanguageTag(),
            ),
            isAccent: true,
            onTap: () {
              navigator.openCartPage();
            },
          )
        : const SizedBox.shrink();
  }
}
