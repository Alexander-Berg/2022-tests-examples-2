// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target

part of 'build.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more informations: https://github.com/rrousselGit/freezed#custom-getters-and-methods');

Build _$BuildFromJson(Map<String, dynamic> json) {
  return _Build.fromJson(json);
}

/// @nodoc
class _$BuildTearOff {
  const _$BuildTearOff();

  _Build call(
      {@JsonKey(name: 'id') required String id,
      @JsonKey(name: 'bugs') required List<Bug> bugs}) {
    return _Build(
      id: id,
      bugs: bugs,
    );
  }

  Build fromJson(Map<String, Object?> json) {
    return Build.fromJson(json);
  }
}

/// @nodoc
const $Build = _$BuildTearOff();

/// @nodoc
mixin _$Build {
  @JsonKey(name: 'id')
  String get id => throw _privateConstructorUsedError;
  @JsonKey(name: 'bugs')
  List<Bug> get bugs => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $BuildCopyWith<Build> get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $BuildCopyWith<$Res> {
  factory $BuildCopyWith(Build value, $Res Function(Build) then) =
      _$BuildCopyWithImpl<$Res>;
  $Res call(
      {@JsonKey(name: 'id') String id, @JsonKey(name: 'bugs') List<Bug> bugs});
}

/// @nodoc
class _$BuildCopyWithImpl<$Res> implements $BuildCopyWith<$Res> {
  _$BuildCopyWithImpl(this._value, this._then);

  final Build _value;
  // ignore: unused_field
  final $Res Function(Build) _then;

  @override
  $Res call({
    Object? id = freezed,
    Object? bugs = freezed,
  }) {
    return _then(_value.copyWith(
      id: id == freezed
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      bugs: bugs == freezed
          ? _value.bugs
          : bugs // ignore: cast_nullable_to_non_nullable
              as List<Bug>,
    ));
  }
}

/// @nodoc
abstract class _$BuildCopyWith<$Res> implements $BuildCopyWith<$Res> {
  factory _$BuildCopyWith(_Build value, $Res Function(_Build) then) =
      __$BuildCopyWithImpl<$Res>;
  @override
  $Res call(
      {@JsonKey(name: 'id') String id, @JsonKey(name: 'bugs') List<Bug> bugs});
}

/// @nodoc
class __$BuildCopyWithImpl<$Res> extends _$BuildCopyWithImpl<$Res>
    implements _$BuildCopyWith<$Res> {
  __$BuildCopyWithImpl(_Build _value, $Res Function(_Build) _then)
      : super(_value, (v) => _then(v as _Build));

  @override
  _Build get _value => super._value as _Build;

  @override
  $Res call({
    Object? id = freezed,
    Object? bugs = freezed,
  }) {
    return _then(_Build(
      id: id == freezed
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      bugs: bugs == freezed
          ? _value.bugs
          : bugs // ignore: cast_nullable_to_non_nullable
              as List<Bug>,
    ));
  }
}

/// @nodoc

@JsonSerializable(explicitToJson: true)
class _$_Build implements _Build {
  const _$_Build(
      {@JsonKey(name: 'id') required this.id,
      @JsonKey(name: 'bugs') required this.bugs});

  factory _$_Build.fromJson(Map<String, dynamic> json) =>
      _$$_BuildFromJson(json);

  @override
  @JsonKey(name: 'id')
  final String id;
  @override
  @JsonKey(name: 'bugs')
  final List<Bug> bugs;

  @override
  String toString() {
    return 'Build(id: $id, bugs: $bugs)';
  }

  @override
  bool operator ==(dynamic other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _Build &&
            const DeepCollectionEquality().equals(other.id, id) &&
            const DeepCollectionEquality().equals(other.bugs, bugs));
  }

  @override
  int get hashCode => Object.hash(
      runtimeType,
      const DeepCollectionEquality().hash(id),
      const DeepCollectionEquality().hash(bugs));

  @JsonKey(ignore: true)
  @override
  _$BuildCopyWith<_Build> get copyWith =>
      __$BuildCopyWithImpl<_Build>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$_BuildToJson(this);
  }
}

abstract class _Build implements Build {
  const factory _Build(
      {@JsonKey(name: 'id') required String id,
      @JsonKey(name: 'bugs') required List<Bug> bugs}) = _$_Build;

  factory _Build.fromJson(Map<String, dynamic> json) = _$_Build.fromJson;

  @override
  @JsonKey(name: 'id')
  String get id;
  @override
  @JsonKey(name: 'bugs')
  List<Bug> get bugs;
  @override
  @JsonKey(ignore: true)
  _$BuildCopyWith<_Build> get copyWith => throw _privateConstructorUsedError;
}
