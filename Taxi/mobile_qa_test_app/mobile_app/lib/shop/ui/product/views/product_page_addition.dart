import 'package:flutter_txm_ui_components/components.dart';
import 'package:models/models.dart';

import '../../../../utils/localization.dart';
import '../../components/shop_section.dart';

class ProductPageAddition extends StatelessWidget {
  final Product product;
  const ProductPageAddition({
    Key? key,
    required this.product,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) => ShopSection(
        child: Column(
          children: [
            YXListItem(
              title: Strings.of(context).aboutProduct,
            ),
            YXListItem(
              borderType: YXListBorderType.none,
              title: Strings.of(context).fullname,
              subtitle: product.fullName,
            ),
            if (product.parameters?.isNotEmpty == true)
              YXListItem(
                borderType: YXListBorderType.none,
                title: Strings.of(context).shortDescription,
              ),
            if (product.parameters?.isNotEmpty == true)
              ...product.parameters
                      ?.map((parameter) => YXListItem(
                            borderType: YXListBorderType.none,
                            title: parameter.name,
                            detailTitle: parameter.value,
                          ))
                      .toList() ??
                  [],
          ],
        ),
      );
}
