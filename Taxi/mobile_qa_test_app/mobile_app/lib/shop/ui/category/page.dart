import 'package:flutter/material.dart';
import 'package:flutter_txm_ui_components/components.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:models/models.dart';

import '../../../utils/localization.dart';
import '../components/shop_horizontal_list_products.dart';
import '../components/shop_scaffold.dart';
import '../components/shop_search.dart';
import '../components/shop_section.dart';
import '../components/user_avatar_button.dart';

class ShopCategoryPage extends ConsumerWidget {
  final Category _category;
  const ShopCategoryPage(this._category, {Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = YXTheme.of<YXThemeData>(context);

    return ShopScaffold(
      appBar: TXMScaffoldAppBar(
        leading: const UserAvatarButton(),
        title: Text(Strings.of(context).shop),
      ),
      slivers: [
        SliverAppBar(
          backgroundColor: theme.colorScheme.minorBackground,
          flexibleSpace: const ShopSection(
            borderRadiusType: ShopSectionBorderRadiusType.bottom,
            child: ShopSearch(),
          ),
        ),
        SliverList(
          delegate: SliverChildListDelegate(
            [
              if (_category.products?.isNotEmpty == true)
                ShopSection(
                  title: Strings.of(context).youWillLikeIt,
                  child: ShopHorizontalListProducts(
                    _category.products ?? <Product>[],
                  ),
                ),
              if (_category.categories?.isNotEmpty == true)
                ..._category.categories
                        ?.map((e) => ShopSection(
                              title: e.title,
                              child: ShopHorizontalListProducts(
                                e.products ?? <Product>[],
                              ),
                            ))
                        .toList() ??
                    [],
            ],
          ),
        ),
      ],
    );
  }
}
