import 'package:flutter/material.dart';
import 'package:flutter_txm_ui_components/components.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

import '../../../cart/providers.dart';
import 'shop_scaffold_actions.dart';

class ShopScaffold extends HookConsumerWidget {
  final List<Widget> slivers;
  final Widget? appBar;
  final List<Widget>? actionItems;
  final Widget? actionButton;

  /// Юзаем для показа заглушки
  final Widget? guard;

  /// Используются slivers.
  /// По умолчанию в [actionButton] находится кнопка "Корзина"
  const ShopScaffold({
    required this.slivers,
    this.actionItems,
    this.actionButton,
    this.appBar,
    this.guard,
    Key? key,
  }) : super(key: key);

  ShopScaffold.list({
    required List<Widget> children,
    this.actionItems,
    this.actionButton,
    this.appBar,
    this.guard,
    Key? key,
  })  : slivers = [
          SliverList(
            delegate: SliverChildListDelegate(
              children,
            ),
          ),
        ],
        super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = YXTheme.of<YXThemeData>(context);
    final isCartEmpty = ref.watch(
      cartStateHolderProvider.select((s) => s.items.isEmpty),
    );

    return TXMScaffold.slivers(
      appBar: appBar,
      actions: isCartEmpty
          ? null
          : ShopScaffoldActions(
              upperItems: actionItems,
              primaryButton: actionButton,
            ),
      slivers: slivers,
      background: theme.colorScheme.minorBackground,
      key: key,
      guard: (guard == null) ? null : SliverFillRemaining(child: guard),
    );
  }
}
