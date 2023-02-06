// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target

part of 'code_page_state.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more informations: https://github.com/rrousselGit/freezed#custom-getters-and-methods');

/// @nodoc
class _$CodePageStateTearOff {
  const _$CodePageStateTearOff();

  _CodePageState call({String code = ''}) {
    return _CodePageState(
      code: code,
    );
  }
}

/// @nodoc
const $CodePageState = _$CodePageStateTearOff();

/// @nodoc
mixin _$CodePageState {
  String get code => throw _privateConstructorUsedError;

  @JsonKey(ignore: true)
  $CodePageStateCopyWith<CodePageState> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $CodePageStateCopyWith<$Res> {
  factory $CodePageStateCopyWith(
          CodePageState value, $Res Function(CodePageState) then) =
      _$CodePageStateCopyWithImpl<$Res>;
  $Res call({String code});
}

/// @nodoc
class _$CodePageStateCopyWithImpl<$Res>
    implements $CodePageStateCopyWith<$Res> {
  _$CodePageStateCopyWithImpl(this._value, this._then);

  final CodePageState _value;
  // ignore: unused_field
  final $Res Function(CodePageState) _then;

  @override
  $Res call({
    Object? code = freezed,
  }) {
    return _then(_value.copyWith(
      code: code == freezed
          ? _value.code
          : code // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
abstract class _$CodePageStateCopyWith<$Res>
    implements $CodePageStateCopyWith<$Res> {
  factory _$CodePageStateCopyWith(
          _CodePageState value, $Res Function(_CodePageState) then) =
      __$CodePageStateCopyWithImpl<$Res>;
  @override
  $Res call({String code});
}

/// @nodoc
class __$CodePageStateCopyWithImpl<$Res>
    extends _$CodePageStateCopyWithImpl<$Res>
    implements _$CodePageStateCopyWith<$Res> {
  __$CodePageStateCopyWithImpl(
      _CodePageState _value, $Res Function(_CodePageState) _then)
      : super(_value, (v) => _then(v as _CodePageState));

  @override
  _CodePageState get _value => super._value as _CodePageState;

  @override
  $Res call({
    Object? code = freezed,
  }) {
    return _then(_CodePageState(
      code: code == freezed
          ? _value.code
          : code // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc

class _$_CodePageState implements _CodePageState {
  const _$_CodePageState({this.code = ''});

  @JsonKey()
  @override
  final String code;

  @override
  String toString() {
    return 'CodePageState(code: $code)';
  }

  @override
  bool operator ==(dynamic other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _CodePageState &&
            const DeepCollectionEquality().equals(other.code, code));
  }

  @override
  int get hashCode =>
      Object.hash(runtimeType, const DeepCollectionEquality().hash(code));

  @JsonKey(ignore: true)
  @override
  _$CodePageStateCopyWith<_CodePageState> get copyWith =>
      __$CodePageStateCopyWithImpl<_CodePageState>(this, _$identity);
}

abstract class _CodePageState implements CodePageState {
  const factory _CodePageState({String code}) = _$_CodePageState;

  @override
  String get code;
  @override
  @JsonKey(ignore: true)
  _$CodePageStateCopyWith<_CodePageState> get copyWith =>
      throw _privateConstructorUsedError;
}
