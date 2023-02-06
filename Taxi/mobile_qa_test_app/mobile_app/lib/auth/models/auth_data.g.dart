// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'auth_data.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$AuthDataSignIn _$$AuthDataSignInFromJson(Map<String, dynamic> json) =>
    _$AuthDataSignIn(
      phone: json['phone'] as String?,
      $type: json['runtimeType'] as String?,
    );

Map<String, dynamic> _$$AuthDataSignInToJson(_$AuthDataSignIn instance) =>
    <String, dynamic>{
      'phone': instance.phone,
      'runtimeType': instance.$type,
    };

_$AuthDataSignUp _$$AuthDataSignUpFromJson(Map<String, dynamic> json) =>
    _$AuthDataSignUp(
      phone: json['phone'] as String?,
      name: json['name'] as String?,
      surname: json['surname'] as String?,
      patronymic: json['patronymic'] as String?,
      $type: json['runtimeType'] as String?,
    );

Map<String, dynamic> _$$AuthDataSignUpToJson(_$AuthDataSignUp instance) =>
    <String, dynamic>{
      'phone': instance.phone,
      'name': instance.name,
      'surname': instance.surname,
      'patronymic': instance.patronymic,
      'runtimeType': instance.$type,
    };
