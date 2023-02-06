import 'package:flutter_txm_ui_components/components.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:models/models.dart';

import '../components/shop_scaffold.dart';
import 'views/product_page_addition.dart';
import 'views/product_page_main_info.dart';

class ProductPage extends ConsumerWidget {
  final Product product;
  const ProductPage(this.product, {Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) => ShopScaffold.list(
        appBar: const TXMScaffoldAppBar(
          leadingIcon: YXIconData.back,
        ),
        children: [
          ProductPageMainInfo(product: product),
          ProductPageAddition(product: product),
        ],
      );
}
