// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target

part of 'signup_page_state.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more informations: https://github.com/rrousselGit/freezed#custom-getters-and-methods');

/// @nodoc
class _$SignUpPageStateTearOff {
  const _$SignUpPageStateTearOff();

  _SignUpPageState call(
      {String name = '', String surname = '', String patronymic = ''}) {
    return _SignUpPageState(
      name: name,
      surname: surname,
      patronymic: patronymic,
    );
  }
}

/// @nodoc
const $SignUpPageState = _$SignUpPageStateTearOff();

/// @nodoc
mixin _$SignUpPageState {
  String get name => throw _privateConstructorUsedError;
  String get surname => throw _privateConstructorUsedError;
  String get patronymic => throw _privateConstructorUsedError;

  @JsonKey(ignore: true)
  $SignUpPageStateCopyWith<SignUpPageState> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $SignUpPageStateCopyWith<$Res> {
  factory $SignUpPageStateCopyWith(
          SignUpPageState value, $Res Function(SignUpPageState) then) =
      _$SignUpPageStateCopyWithImpl<$Res>;
  $Res call({String name, String surname, String patronymic});
}

/// @nodoc
class _$SignUpPageStateCopyWithImpl<$Res>
    implements $SignUpPageStateCopyWith<$Res> {
  _$SignUpPageStateCopyWithImpl(this._value, this._then);

  final SignUpPageState _value;
  // ignore: unused_field
  final $Res Function(SignUpPageState) _then;

  @override
  $Res call({
    Object? name = freezed,
    Object? surname = freezed,
    Object? patronymic = freezed,
  }) {
    return _then(_value.copyWith(
      name: name == freezed
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      surname: surname == freezed
          ? _value.surname
          : surname // ignore: cast_nullable_to_non_nullable
              as String,
      patronymic: patronymic == freezed
          ? _value.patronymic
          : patronymic // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
abstract class _$SignUpPageStateCopyWith<$Res>
    implements $SignUpPageStateCopyWith<$Res> {
  factory _$SignUpPageStateCopyWith(
          _SignUpPageState value, $Res Function(_SignUpPageState) then) =
      __$SignUpPageStateCopyWithImpl<$Res>;
  @override
  $Res call({String name, String surname, String patronymic});
}

/// @nodoc
class __$SignUpPageStateCopyWithImpl<$Res>
    extends _$SignUpPageStateCopyWithImpl<$Res>
    implements _$SignUpPageStateCopyWith<$Res> {
  __$SignUpPageStateCopyWithImpl(
      _SignUpPageState _value, $Res Function(_SignUpPageState) _then)
      : super(_value, (v) => _then(v as _SignUpPageState));

  @override
  _SignUpPageState get _value => super._value as _SignUpPageState;

  @override
  $Res call({
    Object? name = freezed,
    Object? surname = freezed,
    Object? patronymic = freezed,
  }) {
    return _then(_SignUpPageState(
      name: name == freezed
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      surname: surname == freezed
          ? _value.surname
          : surname // ignore: cast_nullable_to_non_nullable
              as String,
      patronymic: patronymic == freezed
          ? _value.patronymic
          : patronymic // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc

class _$_SignUpPageState implements _SignUpPageState {
  const _$_SignUpPageState(
      {this.name = '', this.surname = '', this.patronymic = ''});

  @JsonKey()
  @override
  final String name;
  @JsonKey()
  @override
  final String surname;
  @JsonKey()
  @override
  final String patronymic;

  @override
  String toString() {
    return 'SignUpPageState(name: $name, surname: $surname, patronymic: $patronymic)';
  }

  @override
  bool operator ==(dynamic other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _SignUpPageState &&
            const DeepCollectionEquality().equals(other.name, name) &&
            const DeepCollectionEquality().equals(other.surname, surname) &&
            const DeepCollectionEquality()
                .equals(other.patronymic, patronymic));
  }

  @override
  int get hashCode => Object.hash(
      runtimeType,
      const DeepCollectionEquality().hash(name),
      const DeepCollectionEquality().hash(surname),
      const DeepCollectionEquality().hash(patronymic));

  @JsonKey(ignore: true)
  @override
  _$SignUpPageStateCopyWith<_SignUpPageState> get copyWith =>
      __$SignUpPageStateCopyWithImpl<_SignUpPageState>(this, _$identity);
}

abstract class _SignUpPageState implements SignUpPageState {
  const factory _SignUpPageState(
      {String name, String surname, String patronymic}) = _$_SignUpPageState;

  @override
  String get name;
  @override
  String get surname;
  @override
  String get patronymic;
  @override
  @JsonKey(ignore: true)
  _$SignUpPageStateCopyWith<_SignUpPageState> get copyWith =>
      throw _privateConstructorUsedError;
}
