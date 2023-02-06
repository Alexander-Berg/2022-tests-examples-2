import 'package:intl/intl.dart';

import '../address/domain/address.dart';

extension AddressFormatter on Address {
  String get fullAddress => '$street, $house $corpus $building';
}

extension CurrencyFormatter on num {
  String toPrice({
    required String currencySymbol,
    required String locale,
    required int? fractionDigits,
  }) {
    final currency = NumberFormat.currency(
      locale: locale,
      symbol: currencySymbol,
      decimalDigits: fractionDigits,
    );

    return currency.format(this);
  }
}
