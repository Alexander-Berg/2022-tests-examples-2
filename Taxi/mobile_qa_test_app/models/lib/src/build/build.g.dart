// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'build.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$_Build _$$_BuildFromJson(Map<String, dynamic> json) => _$_Build(
      id: json['id'] as String,
      bugs: (json['bugs'] as List<dynamic>)
          .map((e) => Bug.fromJson(e as Map<String, dynamic>))
          .toList(),
    );

Map<String, dynamic> _$$_BuildToJson(_$_Build instance) => <String, dynamic>{
      'id': instance.id,
      'bugs': instance.bugs.map((e) => e.toJson()).toList(),
    };
