import 'package:freezed_annotation/freezed_annotation.dart';

part 'product.freezed.dart';
part 'product.g.dart';

@freezed
class Product with _$Product {
  const factory Product({
    @JsonKey(name: 'id') required String id,
    @JsonKey(name: 'name') required String name,
    @JsonKey(name: 'full_name') String? fullName,
    @JsonKey(name: 'image_url') required String imageUrl,
    @JsonKey(name: 'price_unit') required PriceUnit priceUnit,
    @JsonKey(name: 'price') required double price,
    @JsonKey(name: 'discounted_price') double? discountedPrice,
    @JsonKey(name: 'count') double? count,
    @JsonKey(name: 'type_count') CountType? typeCount,
    @JsonKey(name: 'parameters') List<ProductParameter>? parameters,
  }) = _Product;

  factory Product.fromJson(Map<String, dynamic> json) =>
      _$ProductFromJson(json);
}

@freezed
class ProductParameter with _$ProductParameter {
  const factory ProductParameter({
    @JsonKey(name: 'id') required String id,
    @JsonKey(name: 'name') required String name,
    @JsonKey(name: 'value') required String value,
  }) = _ProductParameter;

  factory ProductParameter.fromJson(Map<String, dynamic> json) =>
      _$ProductParameterFromJson(json);
}

enum CountType {
  @JsonValue('killograms')
  killograms,
}

enum PriceUnit {
  @JsonValue('rub')
  rub,
}
