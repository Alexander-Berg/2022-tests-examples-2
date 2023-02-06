import 'package:flutter/material.dart';
import 'package:flutter_txm_ui_components/components.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:models/models.dart';

import '../../../utils/navigation/navigation_manager.dart';
import '../components/txm_shop_category.dart';

class ShopCategories extends HookConsumerWidget {
  final List<Category> _categories;
  const ShopCategories(
    this._categories, {
    Key? key,
  }) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) => TXMGridView(
        spanCount: 2,
        children: _categories
            .map(
              (category) => TMXShopCategory(
                category: category,
                onTap: () {
                  ref.read(navigationManagerProvider).openCategory(category);
                },
              ),
            )
            .toList(),
      );
}
