import 'package:flutter/material.dart';
import 'package:flutter_txm_ui_components/components.dart';
import 'package:models/models.dart';

import 'shop_product.dart';

class ShopHorizontalListProducts extends StatelessWidget {
  final List<Product> _products;
  const ShopHorizontalListProducts(
    this._products, {
    Key? key,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) => YXHorizontalList(
        _products.map((product) => ShopProduct(product: product)).toList(),
        horizontalPadding: 0,
      );
}
