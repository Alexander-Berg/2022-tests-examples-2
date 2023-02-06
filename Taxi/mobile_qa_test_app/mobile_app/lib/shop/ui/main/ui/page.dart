import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:flutter_txm_ui_components/components.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

import '../../../../cart/providers.dart';
import '../../../../profile/domain/profile_page_state.dart';
import '../../../../utils/localization.dart';
import '../../components/shop_horizontal_list_products.dart';
import '../../components/shop_scaffold.dart';
import '../../components/shop_search.dart';
import '../../components/shop_section.dart';
import '../../components/user_avatar_button.dart';
import '../../views/shop_categories.dart';
import '../providers.dart';

class ShopMainPage extends HookConsumerWidget {
  const ShopMainPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final categories = ref.watch(
      shopStateHolderProvider.select((s) => s.categories),
    );
    final status = ref.watch(
      shopStateHolderProvider.select((s) => s.status),
    );
    useEffect(
      () {
        ref.read(shopManagerProvider).onInit();
        ref.read(cartManagerProvider).onInit();
      },
      const [],
    );
    final theme = YXTheme.of<YXThemeData>(context);

    return ShopScaffold(
      appBar: TXMScaffoldAppBar(
        leading: const UserAvatarButton(),
        title: Text(Strings.of(context).shop),
      ),
      guard: status == ProgressState.loading
          ? Center(
              child: YXLoadingText(text: Strings.of(context).loading),
            )
          : null,
      slivers: [
        SliverAppBar(
          automaticallyImplyLeading: false,
          backgroundColor: theme.colorScheme.minorBackground,
          flexibleSpace: const ShopSection(
            borderRadiusType: ShopSectionBorderRadiusType.bottom,
            child: ShopSearch(),
          ),
        ),
        if (categories.isNotEmpty)
          SliverList(
            delegate: SliverChildListDelegate(
              [
                ShopSection(
                  title: Strings.of(context).youWillLikeIt,
                  child: ShopHorizontalListProducts(
                    categories.first.categories?.first.products ?? [],
                  ),
                ),
                ShopSection(
                  title: Strings.of(context).categories,
                  child: ShopCategories(categories),
                ),
              ],
            ),
          ),
      ],
    );
  }
}
