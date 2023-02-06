import 'package:freezed_annotation/freezed_annotation.dart';
import 'product.dart';

part 'category.freezed.dart';
part 'category.g.dart';

@freezed
class Category with _$Category {
  const factory Category({
    @JsonKey(name: 'id') required String id,
    @JsonKey(name: 'title') required String title,
    @JsonKey(name: 'image_url') String? imageUrl,
    @JsonKey(name: 'categories') List<Category>? categories,
    @JsonKey(name: 'products') List<Product>? products,
  }) = _Category;

  factory Category.fromJson(Map<String, dynamic> json) =>
      _$CategoryFromJson(json);
}
