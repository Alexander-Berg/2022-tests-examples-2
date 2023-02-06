// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'product.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$_Product _$$_ProductFromJson(Map<String, dynamic> json) => _$_Product(
      id: json['id'] as String,
      name: json['name'] as String,
      fullName: json['full_name'] as String?,
      imageUrl: json['image_url'] as String,
      priceUnit: $enumDecode(_$PriceUnitEnumMap, json['price_unit']),
      price: (json['price'] as num).toDouble(),
      discountedPrice: (json['discounted_price'] as num?)?.toDouble(),
      count: (json['count'] as num?)?.toDouble(),
      typeCount: $enumDecodeNullable(_$CountTypeEnumMap, json['type_count']),
      parameters: (json['parameters'] as List<dynamic>?)
          ?.map((e) => ProductParameter.fromJson(e as Map<String, dynamic>))
          .toList(),
    );

Map<String, dynamic> _$$_ProductToJson(_$_Product instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'full_name': instance.fullName,
      'image_url': instance.imageUrl,
      'price_unit': _$PriceUnitEnumMap[instance.priceUnit],
      'price': instance.price,
      'discounted_price': instance.discountedPrice,
      'count': instance.count,
      'type_count': _$CountTypeEnumMap[instance.typeCount],
      'parameters': instance.parameters?.map((e) => e.toJson()).toList(),
    };

const _$PriceUnitEnumMap = {
  PriceUnit.rub: 'rub',
};

const _$CountTypeEnumMap = {
  CountType.killograms: 'killograms',
};

_$_ProductParameter _$$_ProductParameterFromJson(Map<String, dynamic> json) =>
    _$_ProductParameter(
      id: json['id'] as String,
      name: json['name'] as String,
      value: json['value'] as String,
    );

Map<String, dynamic> _$$_ProductParameterToJson(_$_ProductParameter instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'value': instance.value,
    };
