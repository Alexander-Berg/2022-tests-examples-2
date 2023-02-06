// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target

part of 'product.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more informations: https://github.com/rrousselGit/freezed#custom-getters-and-methods');

Product _$ProductFromJson(Map<String, dynamic> json) {
  return _Product.fromJson(json);
}

/// @nodoc
class _$ProductTearOff {
  const _$ProductTearOff();

  _Product call(
      {@JsonKey(name: 'id') required String id,
      @JsonKey(name: 'name') required String name,
      @JsonKey(name: 'full_name') String? fullName,
      @JsonKey(name: 'image_url') required String imageUrl,
      @JsonKey(name: 'price_unit') required PriceUnit priceUnit,
      @JsonKey(name: 'price') required double price,
      @JsonKey(name: 'discounted_price') double? discountedPrice,
      @JsonKey(name: 'count') double? count,
      @JsonKey(name: 'type_count') CountType? typeCount,
      @JsonKey(name: 'parameters') List<ProductParameter>? parameters}) {
    return _Product(
      id: id,
      name: name,
      fullName: fullName,
      imageUrl: imageUrl,
      priceUnit: priceUnit,
      price: price,
      discountedPrice: discountedPrice,
      count: count,
      typeCount: typeCount,
      parameters: parameters,
    );
  }

  Product fromJson(Map<String, Object?> json) {
    return Product.fromJson(json);
  }
}

/// @nodoc
const $Product = _$ProductTearOff();

/// @nodoc
mixin _$Product {
  @JsonKey(name: 'id')
  String get id => throw _privateConstructorUsedError;
  @JsonKey(name: 'name')
  String get name => throw _privateConstructorUsedError;
  @JsonKey(name: 'full_name')
  String? get fullName => throw _privateConstructorUsedError;
  @JsonKey(name: 'image_url')
  String get imageUrl => throw _privateConstructorUsedError;
  @JsonKey(name: 'price_unit')
  PriceUnit get priceUnit => throw _privateConstructorUsedError;
  @JsonKey(name: 'price')
  double get price => throw _privateConstructorUsedError;
  @JsonKey(name: 'discounted_price')
  double? get discountedPrice => throw _privateConstructorUsedError;
  @JsonKey(name: 'count')
  double? get count => throw _privateConstructorUsedError;
  @JsonKey(name: 'type_count')
  CountType? get typeCount => throw _privateConstructorUsedError;
  @JsonKey(name: 'parameters')
  List<ProductParameter>? get parameters => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $ProductCopyWith<Product> get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ProductCopyWith<$Res> {
  factory $ProductCopyWith(Product value, $Res Function(Product) then) =
      _$ProductCopyWithImpl<$Res>;
  $Res call(
      {@JsonKey(name: 'id') String id,
      @JsonKey(name: 'name') String name,
      @JsonKey(name: 'full_name') String? fullName,
      @JsonKey(name: 'image_url') String imageUrl,
      @JsonKey(name: 'price_unit') PriceUnit priceUnit,
      @JsonKey(name: 'price') double price,
      @JsonKey(name: 'discounted_price') double? discountedPrice,
      @JsonKey(name: 'count') double? count,
      @JsonKey(name: 'type_count') CountType? typeCount,
      @JsonKey(name: 'parameters') List<ProductParameter>? parameters});
}

/// @nodoc
class _$ProductCopyWithImpl<$Res> implements $ProductCopyWith<$Res> {
  _$ProductCopyWithImpl(this._value, this._then);

  final Product _value;
  // ignore: unused_field
  final $Res Function(Product) _then;

  @override
  $Res call({
    Object? id = freezed,
    Object? name = freezed,
    Object? fullName = freezed,
    Object? imageUrl = freezed,
    Object? priceUnit = freezed,
    Object? price = freezed,
    Object? discountedPrice = freezed,
    Object? count = freezed,
    Object? typeCount = freezed,
    Object? parameters = freezed,
  }) {
    return _then(_value.copyWith(
      id: id == freezed
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      name: name == freezed
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      fullName: fullName == freezed
          ? _value.fullName
          : fullName // ignore: cast_nullable_to_non_nullable
              as String?,
      imageUrl: imageUrl == freezed
          ? _value.imageUrl
          : imageUrl // ignore: cast_nullable_to_non_nullable
              as String,
      priceUnit: priceUnit == freezed
          ? _value.priceUnit
          : priceUnit // ignore: cast_nullable_to_non_nullable
              as PriceUnit,
      price: price == freezed
          ? _value.price
          : price // ignore: cast_nullable_to_non_nullable
              as double,
      discountedPrice: discountedPrice == freezed
          ? _value.discountedPrice
          : discountedPrice // ignore: cast_nullable_to_non_nullable
              as double?,
      count: count == freezed
          ? _value.count
          : count // ignore: cast_nullable_to_non_nullable
              as double?,
      typeCount: typeCount == freezed
          ? _value.typeCount
          : typeCount // ignore: cast_nullable_to_non_nullable
              as CountType?,
      parameters: parameters == freezed
          ? _value.parameters
          : parameters // ignore: cast_nullable_to_non_nullable
              as List<ProductParameter>?,
    ));
  }
}

/// @nodoc
abstract class _$ProductCopyWith<$Res> implements $ProductCopyWith<$Res> {
  factory _$ProductCopyWith(_Product value, $Res Function(_Product) then) =
      __$ProductCopyWithImpl<$Res>;
  @override
  $Res call(
      {@JsonKey(name: 'id') String id,
      @JsonKey(name: 'name') String name,
      @JsonKey(name: 'full_name') String? fullName,
      @JsonKey(name: 'image_url') String imageUrl,
      @JsonKey(name: 'price_unit') PriceUnit priceUnit,
      @JsonKey(name: 'price') double price,
      @JsonKey(name: 'discounted_price') double? discountedPrice,
      @JsonKey(name: 'count') double? count,
      @JsonKey(name: 'type_count') CountType? typeCount,
      @JsonKey(name: 'parameters') List<ProductParameter>? parameters});
}

/// @nodoc
class __$ProductCopyWithImpl<$Res> extends _$ProductCopyWithImpl<$Res>
    implements _$ProductCopyWith<$Res> {
  __$ProductCopyWithImpl(_Product _value, $Res Function(_Product) _then)
      : super(_value, (v) => _then(v as _Product));

  @override
  _Product get _value => super._value as _Product;

  @override
  $Res call({
    Object? id = freezed,
    Object? name = freezed,
    Object? fullName = freezed,
    Object? imageUrl = freezed,
    Object? priceUnit = freezed,
    Object? price = freezed,
    Object? discountedPrice = freezed,
    Object? count = freezed,
    Object? typeCount = freezed,
    Object? parameters = freezed,
  }) {
    return _then(_Product(
      id: id == freezed
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      name: name == freezed
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      fullName: fullName == freezed
          ? _value.fullName
          : fullName // ignore: cast_nullable_to_non_nullable
              as String?,
      imageUrl: imageUrl == freezed
          ? _value.imageUrl
          : imageUrl // ignore: cast_nullable_to_non_nullable
              as String,
      priceUnit: priceUnit == freezed
          ? _value.priceUnit
          : priceUnit // ignore: cast_nullable_to_non_nullable
              as PriceUnit,
      price: price == freezed
          ? _value.price
          : price // ignore: cast_nullable_to_non_nullable
              as double,
      discountedPrice: discountedPrice == freezed
          ? _value.discountedPrice
          : discountedPrice // ignore: cast_nullable_to_non_nullable
              as double?,
      count: count == freezed
          ? _value.count
          : count // ignore: cast_nullable_to_non_nullable
              as double?,
      typeCount: typeCount == freezed
          ? _value.typeCount
          : typeCount // ignore: cast_nullable_to_non_nullable
              as CountType?,
      parameters: parameters == freezed
          ? _value.parameters
          : parameters // ignore: cast_nullable_to_non_nullable
              as List<ProductParameter>?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$_Product implements _Product {
  const _$_Product(
      {@JsonKey(name: 'id') required this.id,
      @JsonKey(name: 'name') required this.name,
      @JsonKey(name: 'full_name') this.fullName,
      @JsonKey(name: 'image_url') required this.imageUrl,
      @JsonKey(name: 'price_unit') required this.priceUnit,
      @JsonKey(name: 'price') required this.price,
      @JsonKey(name: 'discounted_price') this.discountedPrice,
      @JsonKey(name: 'count') this.count,
      @JsonKey(name: 'type_count') this.typeCount,
      @JsonKey(name: 'parameters') this.parameters});

  factory _$_Product.fromJson(Map<String, dynamic> json) =>
      _$$_ProductFromJson(json);

  @override
  @JsonKey(name: 'id')
  final String id;
  @override
  @JsonKey(name: 'name')
  final String name;
  @override
  @JsonKey(name: 'full_name')
  final String? fullName;
  @override
  @JsonKey(name: 'image_url')
  final String imageUrl;
  @override
  @JsonKey(name: 'price_unit')
  final PriceUnit priceUnit;
  @override
  @JsonKey(name: 'price')
  final double price;
  @override
  @JsonKey(name: 'discounted_price')
  final double? discountedPrice;
  @override
  @JsonKey(name: 'count')
  final double? count;
  @override
  @JsonKey(name: 'type_count')
  final CountType? typeCount;
  @override
  @JsonKey(name: 'parameters')
  final List<ProductParameter>? parameters;

  @override
  String toString() {
    return 'Product(id: $id, name: $name, fullName: $fullName, imageUrl: $imageUrl, priceUnit: $priceUnit, price: $price, discountedPrice: $discountedPrice, count: $count, typeCount: $typeCount, parameters: $parameters)';
  }

  @override
  bool operator ==(dynamic other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _Product &&
            const DeepCollectionEquality().equals(other.id, id) &&
            const DeepCollectionEquality().equals(other.name, name) &&
            const DeepCollectionEquality().equals(other.fullName, fullName) &&
            const DeepCollectionEquality().equals(other.imageUrl, imageUrl) &&
            const DeepCollectionEquality().equals(other.priceUnit, priceUnit) &&
            const DeepCollectionEquality().equals(other.price, price) &&
            const DeepCollectionEquality()
                .equals(other.discountedPrice, discountedPrice) &&
            const DeepCollectionEquality().equals(other.count, count) &&
            const DeepCollectionEquality().equals(other.typeCount, typeCount) &&
            const DeepCollectionEquality()
                .equals(other.parameters, parameters));
  }

  @override
  int get hashCode => Object.hash(
      runtimeType,
      const DeepCollectionEquality().hash(id),
      const DeepCollectionEquality().hash(name),
      const DeepCollectionEquality().hash(fullName),
      const DeepCollectionEquality().hash(imageUrl),
      const DeepCollectionEquality().hash(priceUnit),
      const DeepCollectionEquality().hash(price),
      const DeepCollectionEquality().hash(discountedPrice),
      const DeepCollectionEquality().hash(count),
      const DeepCollectionEquality().hash(typeCount),
      const DeepCollectionEquality().hash(parameters));

  @JsonKey(ignore: true)
  @override
  _$ProductCopyWith<_Product> get copyWith =>
      __$ProductCopyWithImpl<_Product>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$_ProductToJson(this);
  }
}

abstract class _Product implements Product {
  const factory _Product(
          {@JsonKey(name: 'id') required String id,
          @JsonKey(name: 'name') required String name,
          @JsonKey(name: 'full_name') String? fullName,
          @JsonKey(name: 'image_url') required String imageUrl,
          @JsonKey(name: 'price_unit') required PriceUnit priceUnit,
          @JsonKey(name: 'price') required double price,
          @JsonKey(name: 'discounted_price') double? discountedPrice,
          @JsonKey(name: 'count') double? count,
          @JsonKey(name: 'type_count') CountType? typeCount,
          @JsonKey(name: 'parameters') List<ProductParameter>? parameters}) =
      _$_Product;

  factory _Product.fromJson(Map<String, dynamic> json) = _$_Product.fromJson;

  @override
  @JsonKey(name: 'id')
  String get id;
  @override
  @JsonKey(name: 'name')
  String get name;
  @override
  @JsonKey(name: 'full_name')
  String? get fullName;
  @override
  @JsonKey(name: 'image_url')
  String get imageUrl;
  @override
  @JsonKey(name: 'price_unit')
  PriceUnit get priceUnit;
  @override
  @JsonKey(name: 'price')
  double get price;
  @override
  @JsonKey(name: 'discounted_price')
  double? get discountedPrice;
  @override
  @JsonKey(name: 'count')
  double? get count;
  @override
  @JsonKey(name: 'type_count')
  CountType? get typeCount;
  @override
  @JsonKey(name: 'parameters')
  List<ProductParameter>? get parameters;
  @override
  @JsonKey(ignore: true)
  _$ProductCopyWith<_Product> get copyWith =>
      throw _privateConstructorUsedError;
}

ProductParameter _$ProductParameterFromJson(Map<String, dynamic> json) {
  return _ProductParameter.fromJson(json);
}

/// @nodoc
class _$ProductParameterTearOff {
  const _$ProductParameterTearOff();

  _ProductParameter call(
      {@JsonKey(name: 'id') required String id,
      @JsonKey(name: 'name') required String name,
      @JsonKey(name: 'value') required String value}) {
    return _ProductParameter(
      id: id,
      name: name,
      value: value,
    );
  }

  ProductParameter fromJson(Map<String, Object?> json) {
    return ProductParameter.fromJson(json);
  }
}

/// @nodoc
const $ProductParameter = _$ProductParameterTearOff();

/// @nodoc
mixin _$ProductParameter {
  @JsonKey(name: 'id')
  String get id => throw _privateConstructorUsedError;
  @JsonKey(name: 'name')
  String get name => throw _privateConstructorUsedError;
  @JsonKey(name: 'value')
  String get value => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $ProductParameterCopyWith<ProductParameter> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ProductParameterCopyWith<$Res> {
  factory $ProductParameterCopyWith(
          ProductParameter value, $Res Function(ProductParameter) then) =
      _$ProductParameterCopyWithImpl<$Res>;
  $Res call(
      {@JsonKey(name: 'id') String id,
      @JsonKey(name: 'name') String name,
      @JsonKey(name: 'value') String value});
}

/// @nodoc
class _$ProductParameterCopyWithImpl<$Res>
    implements $ProductParameterCopyWith<$Res> {
  _$ProductParameterCopyWithImpl(this._value, this._then);

  final ProductParameter _value;
  // ignore: unused_field
  final $Res Function(ProductParameter) _then;

  @override
  $Res call({
    Object? id = freezed,
    Object? name = freezed,
    Object? value = freezed,
  }) {
    return _then(_value.copyWith(
      id: id == freezed
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      name: name == freezed
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      value: value == freezed
          ? _value.value
          : value // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
abstract class _$ProductParameterCopyWith<$Res>
    implements $ProductParameterCopyWith<$Res> {
  factory _$ProductParameterCopyWith(
          _ProductParameter value, $Res Function(_ProductParameter) then) =
      __$ProductParameterCopyWithImpl<$Res>;
  @override
  $Res call(
      {@JsonKey(name: 'id') String id,
      @JsonKey(name: 'name') String name,
      @JsonKey(name: 'value') String value});
}

/// @nodoc
class __$ProductParameterCopyWithImpl<$Res>
    extends _$ProductParameterCopyWithImpl<$Res>
    implements _$ProductParameterCopyWith<$Res> {
  __$ProductParameterCopyWithImpl(
      _ProductParameter _value, $Res Function(_ProductParameter) _then)
      : super(_value, (v) => _then(v as _ProductParameter));

  @override
  _ProductParameter get _value => super._value as _ProductParameter;

  @override
  $Res call({
    Object? id = freezed,
    Object? name = freezed,
    Object? value = freezed,
  }) {
    return _then(_ProductParameter(
      id: id == freezed
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      name: name == freezed
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      value: value == freezed
          ? _value.value
          : value // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$_ProductParameter implements _ProductParameter {
  const _$_ProductParameter(
      {@JsonKey(name: 'id') required this.id,
      @JsonKey(name: 'name') required this.name,
      @JsonKey(name: 'value') required this.value});

  factory _$_ProductParameter.fromJson(Map<String, dynamic> json) =>
      _$$_ProductParameterFromJson(json);

  @override
  @JsonKey(name: 'id')
  final String id;
  @override
  @JsonKey(name: 'name')
  final String name;
  @override
  @JsonKey(name: 'value')
  final String value;

  @override
  String toString() {
    return 'ProductParameter(id: $id, name: $name, value: $value)';
  }

  @override
  bool operator ==(dynamic other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _ProductParameter &&
            const DeepCollectionEquality().equals(other.id, id) &&
            const DeepCollectionEquality().equals(other.name, name) &&
            const DeepCollectionEquality().equals(other.value, value));
  }

  @override
  int get hashCode => Object.hash(
      runtimeType,
      const DeepCollectionEquality().hash(id),
      const DeepCollectionEquality().hash(name),
      const DeepCollectionEquality().hash(value));

  @JsonKey(ignore: true)
  @override
  _$ProductParameterCopyWith<_ProductParameter> get copyWith =>
      __$ProductParameterCopyWithImpl<_ProductParameter>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$_ProductParameterToJson(this);
  }
}

abstract class _ProductParameter implements ProductParameter {
  const factory _ProductParameter(
      {@JsonKey(name: 'id') required String id,
      @JsonKey(name: 'name') required String name,
      @JsonKey(name: 'value') required String value}) = _$_ProductParameter;

  factory _ProductParameter.fromJson(Map<String, dynamic> json) =
      _$_ProductParameter.fromJson;

  @override
  @JsonKey(name: 'id')
  String get id;
  @override
  @JsonKey(name: 'name')
  String get name;
  @override
  @JsonKey(name: 'value')
  String get value;
  @override
  @JsonKey(ignore: true)
  _$ProductParameterCopyWith<_ProductParameter> get copyWith =>
      throw _privateConstructorUsedError;
}
