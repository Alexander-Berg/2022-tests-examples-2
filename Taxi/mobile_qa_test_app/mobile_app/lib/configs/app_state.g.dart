// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'app_state.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$_AppState _$$_AppStateFromJson(Map<String, dynamic> json) => _$_AppState(
      theme: $enumDecodeNullable(_$AppStateThemeEnumMap, json['theme']) ??
          AppStateTheme.light,
    );

Map<String, dynamic> _$$_AppStateToJson(_$_AppState instance) =>
    <String, dynamic>{
      'theme': _$AppStateThemeEnumMap[instance.theme],
    };

const _$AppStateThemeEnumMap = {
  AppStateTheme.dark: 'dark',
  AppStateTheme.light: 'light',
};
