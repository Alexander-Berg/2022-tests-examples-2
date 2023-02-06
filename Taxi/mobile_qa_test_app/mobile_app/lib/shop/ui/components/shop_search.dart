import 'package:flutter/material.dart';
import 'package:flutter_txm_ui_components/components.dart';
import '../../../utils/localization.dart';

class ShopSearch extends StatelessWidget {
  const ShopSearch({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) => YXListInput(
        useHintAsPlaceholder: true,
        placeholderHasDots: false,
        hint: Strings.of(context).findInShop,
        borderType: YXListBorderType.none,
      );
}
