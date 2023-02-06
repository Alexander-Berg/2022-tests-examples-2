// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target

part of 'phone_page_state.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more informations: https://github.com/rrousselGit/freezed#custom-getters-and-methods');

/// @nodoc
class _$PhonePageStateTearOff {
  const _$PhonePageStateTearOff();

  _PhonePageState call({required String phone}) {
    return _PhonePageState(
      phone: phone,
    );
  }
}

/// @nodoc
const $PhonePageState = _$PhonePageStateTearOff();

/// @nodoc
mixin _$PhonePageState {
  String get phone => throw _privateConstructorUsedError;

  @JsonKey(ignore: true)
  $PhonePageStateCopyWith<PhonePageState> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $PhonePageStateCopyWith<$Res> {
  factory $PhonePageStateCopyWith(
          PhonePageState value, $Res Function(PhonePageState) then) =
      _$PhonePageStateCopyWithImpl<$Res>;
  $Res call({String phone});
}

/// @nodoc
class _$PhonePageStateCopyWithImpl<$Res>
    implements $PhonePageStateCopyWith<$Res> {
  _$PhonePageStateCopyWithImpl(this._value, this._then);

  final PhonePageState _value;
  // ignore: unused_field
  final $Res Function(PhonePageState) _then;

  @override
  $Res call({
    Object? phone = freezed,
  }) {
    return _then(_value.copyWith(
      phone: phone == freezed
          ? _value.phone
          : phone // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
abstract class _$PhonePageStateCopyWith<$Res>
    implements $PhonePageStateCopyWith<$Res> {
  factory _$PhonePageStateCopyWith(
          _PhonePageState value, $Res Function(_PhonePageState) then) =
      __$PhonePageStateCopyWithImpl<$Res>;
  @override
  $Res call({String phone});
}

/// @nodoc
class __$PhonePageStateCopyWithImpl<$Res>
    extends _$PhonePageStateCopyWithImpl<$Res>
    implements _$PhonePageStateCopyWith<$Res> {
  __$PhonePageStateCopyWithImpl(
      _PhonePageState _value, $Res Function(_PhonePageState) _then)
      : super(_value, (v) => _then(v as _PhonePageState));

  @override
  _PhonePageState get _value => super._value as _PhonePageState;

  @override
  $Res call({
    Object? phone = freezed,
  }) {
    return _then(_PhonePageState(
      phone: phone == freezed
          ? _value.phone
          : phone // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc

class _$_PhonePageState implements _PhonePageState {
  const _$_PhonePageState({required this.phone});

  @override
  final String phone;

  @override
  String toString() {
    return 'PhonePageState(phone: $phone)';
  }

  @override
  bool operator ==(dynamic other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _PhonePageState &&
            const DeepCollectionEquality().equals(other.phone, phone));
  }

  @override
  int get hashCode =>
      Object.hash(runtimeType, const DeepCollectionEquality().hash(phone));

  @JsonKey(ignore: true)
  @override
  _$PhonePageStateCopyWith<_PhonePageState> get copyWith =>
      __$PhonePageStateCopyWithImpl<_PhonePageState>(this, _$identity);
}

abstract class _PhonePageState implements PhonePageState {
  const factory _PhonePageState({required String phone}) = _$_PhonePageState;

  @override
  String get phone;
  @override
  @JsonKey(ignore: true)
  _$PhonePageStateCopyWith<_PhonePageState> get copyWith =>
      throw _privateConstructorUsedError;
}
