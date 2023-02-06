// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'address.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$_Address _$$_AddressFromJson(Map<String, dynamic> json) => _$_Address(
      city: json['city'] as String,
      street: json['street'] as String,
      house: json['house'] as String,
      corpus: json['corpus'] as String? ?? '',
      building: json['building'] as String? ?? '',
    );

Map<String, dynamic> _$$_AddressToJson(_$_Address instance) =>
    <String, dynamic>{
      'city': instance.city,
      'street': instance.street,
      'house': instance.house,
      'corpus': instance.corpus,
      'building': instance.building,
    };
