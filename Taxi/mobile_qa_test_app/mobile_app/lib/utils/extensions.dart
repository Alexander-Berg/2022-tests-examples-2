import 'package:flutter_txm_ui_components/components.dart';
import 'package:models/models.dart';

import 'localization.dart';

extension ProductCount on Product {
  String amountOf(BuildContext context) {
    switch (typeCount) {
      case CountType.killograms:
        return '$count ${Strings.of(context).killograms}';
      case null:
        return '';
    }
  }
}
