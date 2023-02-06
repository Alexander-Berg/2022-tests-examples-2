import 'package:freezed_annotation/freezed_annotation.dart';

part 'bug.freezed.dart';
part 'bug.g.dart';

@freezed
class Bug with _$Bug {
  const factory Bug({
    @JsonKey(name: 'id') required String id,
  }) = _Bug;

  factory Bug.fromJson(Map<String, dynamic> json) => _$BugFromJson(json);
}

class BugIds {
  static const shopProductOnIncrementDouble =
      'shop/product/on_increment/double';
  static const phoneTitleMisspell = 'phone/title/misspell';
  static const supportAnswerOnInitCrush = 'support/answer/on_init/crush';
  static const profileOnSaveDoesNotWork = 'profile/on_save/does_not_work';
  static const paymentOptionsOnTapFreezed = 'payment/options/on_tap/freezed';
  static const cardCvvInputLength4 = 'card/cvv/input/length_4';
  static const cartClearDoesNotWork = 'cart/clear/does_not_work';
  static const shopProductOnDecrementInverse =
      'shop/product/on_decrement/inverse';
  static const navigateFromCategoryToShop =
      'shop/navigation/from_category_to_shop';
}
