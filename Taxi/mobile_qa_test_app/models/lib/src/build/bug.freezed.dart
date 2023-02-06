// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target

part of 'bug.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more informations: https://github.com/rrousselGit/freezed#custom-getters-and-methods');

Bug _$BugFromJson(Map<String, dynamic> json) {
  return _Bug.fromJson(json);
}

/// @nodoc
class _$BugTearOff {
  const _$BugTearOff();

  _Bug call({@JsonKey(name: 'id') required String id}) {
    return _Bug(
      id: id,
    );
  }

  Bug fromJson(Map<String, Object?> json) {
    return Bug.fromJson(json);
  }
}

/// @nodoc
const $Bug = _$BugTearOff();

/// @nodoc
mixin _$Bug {
  @JsonKey(name: 'id')
  String get id => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $BugCopyWith<Bug> get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $BugCopyWith<$Res> {
  factory $BugCopyWith(Bug value, $Res Function(Bug) then) =
      _$BugCopyWithImpl<$Res>;
  $Res call({@JsonKey(name: 'id') String id});
}

/// @nodoc
class _$BugCopyWithImpl<$Res> implements $BugCopyWith<$Res> {
  _$BugCopyWithImpl(this._value, this._then);

  final Bug _value;
  // ignore: unused_field
  final $Res Function(Bug) _then;

  @override
  $Res call({
    Object? id = freezed,
  }) {
    return _then(_value.copyWith(
      id: id == freezed
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
abstract class _$BugCopyWith<$Res> implements $BugCopyWith<$Res> {
  factory _$BugCopyWith(_Bug value, $Res Function(_Bug) then) =
      __$BugCopyWithImpl<$Res>;
  @override
  $Res call({@JsonKey(name: 'id') String id});
}

/// @nodoc
class __$BugCopyWithImpl<$Res> extends _$BugCopyWithImpl<$Res>
    implements _$BugCopyWith<$Res> {
  __$BugCopyWithImpl(_Bug _value, $Res Function(_Bug) _then)
      : super(_value, (v) => _then(v as _Bug));

  @override
  _Bug get _value => super._value as _Bug;

  @override
  $Res call({
    Object? id = freezed,
  }) {
    return _then(_Bug(
      id: id == freezed
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$_Bug implements _Bug {
  const _$_Bug({@JsonKey(name: 'id') required this.id});

  factory _$_Bug.fromJson(Map<String, dynamic> json) => _$$_BugFromJson(json);

  @override
  @JsonKey(name: 'id')
  final String id;

  @override
  String toString() {
    return 'Bug(id: $id)';
  }

  @override
  bool operator ==(dynamic other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _Bug &&
            const DeepCollectionEquality().equals(other.id, id));
  }

  @override
  int get hashCode =>
      Object.hash(runtimeType, const DeepCollectionEquality().hash(id));

  @JsonKey(ignore: true)
  @override
  _$BugCopyWith<_Bug> get copyWith =>
      __$BugCopyWithImpl<_Bug>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$_BugToJson(this);
  }
}

abstract class _Bug implements Bug {
  const factory _Bug({@JsonKey(name: 'id') required String id}) = _$_Bug;

  factory _Bug.fromJson(Map<String, dynamic> json) = _$_Bug.fromJson;

  @override
  @JsonKey(name: 'id')
  String get id;
  @override
  @JsonKey(ignore: true)
  _$BugCopyWith<_Bug> get copyWith => throw _privateConstructorUsedError;
}
