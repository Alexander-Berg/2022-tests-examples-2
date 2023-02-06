// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'cart_state.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$_CartState _$$_CartStateFromJson(Map<String, dynamic> json) => _$_CartState(
      (json['items'] as List<dynamic>)
          .map((e) => CartItem.fromJson(e as Map<String, dynamic>))
          .toList(),
      json['userPhone'] as String?,
    );

Map<String, dynamic> _$$_CartStateToJson(_$_CartState instance) =>
    <String, dynamic>{
      'items': instance.items.map((e) => e.toJson()).toList(),
      'userPhone': instance.userPhone,
    };

_$_CartItem _$$_CartItemFromJson(Map<String, dynamic> json) => _$_CartItem(
      product: Product.fromJson(json['product'] as Map<String, dynamic>),
      count: json['count'] as int? ?? 1,
    );

Map<String, dynamic> _$$_CartItemToJson(_$_CartItem instance) =>
    <String, dynamic>{
      'product': instance.product.toJson(),
      'count': instance.count,
    };
