// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'card.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$_Card _$$_CardFromJson(Map<String, dynamic> json) => _$_Card(
      cardNumber: json['card_number'] as String,
      cvv: json['cvv'] as String,
      owner: json['owner'] as String,
      validityPeriod: DateTime.parse(json['validity_period'] as String),
    );

Map<String, dynamic> _$$_CardToJson(_$_Card instance) => <String, dynamic>{
      'card_number': instance.cardNumber,
      'cvv': instance.cvv,
      'owner': instance.owner,
      'validity_period': instance.validityPeriod.toIso8601String(),
    };
