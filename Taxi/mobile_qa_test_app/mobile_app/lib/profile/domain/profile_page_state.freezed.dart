// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target

part of 'profile_page_state.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more informations: https://github.com/rrousselGit/freezed#custom-getters-and-methods');

/// @nodoc
class _$ProfilePageStateTearOff {
  const _$ProfilePageStateTearOff();

  _ProfilePageState call(
      {String name = '',
      String surname = '',
      String patronymic = '',
      String phone = '',
      ProgressState loadingState = ProgressState.loading,
      ProgressState savingState = ProgressState.done}) {
    return _ProfilePageState(
      name: name,
      surname: surname,
      patronymic: patronymic,
      phone: phone,
      loadingState: loadingState,
      savingState: savingState,
    );
  }
}

/// @nodoc
const $ProfilePageState = _$ProfilePageStateTearOff();

/// @nodoc
mixin _$ProfilePageState {
  String get name => throw _privateConstructorUsedError;
  String get surname => throw _privateConstructorUsedError;
  String get patronymic => throw _privateConstructorUsedError;
  String get phone => throw _privateConstructorUsedError;
  ProgressState get loadingState => throw _privateConstructorUsedError;
  ProgressState get savingState => throw _privateConstructorUsedError;

  @JsonKey(ignore: true)
  $ProfilePageStateCopyWith<ProfilePageState> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ProfilePageStateCopyWith<$Res> {
  factory $ProfilePageStateCopyWith(
          ProfilePageState value, $Res Function(ProfilePageState) then) =
      _$ProfilePageStateCopyWithImpl<$Res>;
  $Res call(
      {String name,
      String surname,
      String patronymic,
      String phone,
      ProgressState loadingState,
      ProgressState savingState});
}

/// @nodoc
class _$ProfilePageStateCopyWithImpl<$Res>
    implements $ProfilePageStateCopyWith<$Res> {
  _$ProfilePageStateCopyWithImpl(this._value, this._then);

  final ProfilePageState _value;
  // ignore: unused_field
  final $Res Function(ProfilePageState) _then;

  @override
  $Res call({
    Object? name = freezed,
    Object? surname = freezed,
    Object? patronymic = freezed,
    Object? phone = freezed,
    Object? loadingState = freezed,
    Object? savingState = freezed,
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
      phone: phone == freezed
          ? _value.phone
          : phone // ignore: cast_nullable_to_non_nullable
              as String,
      loadingState: loadingState == freezed
          ? _value.loadingState
          : loadingState // ignore: cast_nullable_to_non_nullable
              as ProgressState,
      savingState: savingState == freezed
          ? _value.savingState
          : savingState // ignore: cast_nullable_to_non_nullable
              as ProgressState,
    ));
  }
}

/// @nodoc
abstract class _$ProfilePageStateCopyWith<$Res>
    implements $ProfilePageStateCopyWith<$Res> {
  factory _$ProfilePageStateCopyWith(
          _ProfilePageState value, $Res Function(_ProfilePageState) then) =
      __$ProfilePageStateCopyWithImpl<$Res>;
  @override
  $Res call(
      {String name,
      String surname,
      String patronymic,
      String phone,
      ProgressState loadingState,
      ProgressState savingState});
}

/// @nodoc
class __$ProfilePageStateCopyWithImpl<$Res>
    extends _$ProfilePageStateCopyWithImpl<$Res>
    implements _$ProfilePageStateCopyWith<$Res> {
  __$ProfilePageStateCopyWithImpl(
      _ProfilePageState _value, $Res Function(_ProfilePageState) _then)
      : super(_value, (v) => _then(v as _ProfilePageState));

  @override
  _ProfilePageState get _value => super._value as _ProfilePageState;

  @override
  $Res call({
    Object? name = freezed,
    Object? surname = freezed,
    Object? patronymic = freezed,
    Object? phone = freezed,
    Object? loadingState = freezed,
    Object? savingState = freezed,
  }) {
    return _then(_ProfilePageState(
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
      phone: phone == freezed
          ? _value.phone
          : phone // ignore: cast_nullable_to_non_nullable
              as String,
      loadingState: loadingState == freezed
          ? _value.loadingState
          : loadingState // ignore: cast_nullable_to_non_nullable
              as ProgressState,
      savingState: savingState == freezed
          ? _value.savingState
          : savingState // ignore: cast_nullable_to_non_nullable
              as ProgressState,
    ));
  }
}

/// @nodoc

class _$_ProfilePageState implements _ProfilePageState {
  const _$_ProfilePageState(
      {this.name = '',
      this.surname = '',
      this.patronymic = '',
      this.phone = '',
      this.loadingState = ProgressState.loading,
      this.savingState = ProgressState.done});

  @JsonKey()
  @override
  final String name;
  @JsonKey()
  @override
  final String surname;
  @JsonKey()
  @override
  final String patronymic;
  @JsonKey()
  @override
  final String phone;
  @JsonKey()
  @override
  final ProgressState loadingState;
  @JsonKey()
  @override
  final ProgressState savingState;

  @override
  String toString() {
    return 'ProfilePageState(name: $name, surname: $surname, patronymic: $patronymic, phone: $phone, loadingState: $loadingState, savingState: $savingState)';
  }

  @override
  bool operator ==(dynamic other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _ProfilePageState &&
            const DeepCollectionEquality().equals(other.name, name) &&
            const DeepCollectionEquality().equals(other.surname, surname) &&
            const DeepCollectionEquality()
                .equals(other.patronymic, patronymic) &&
            const DeepCollectionEquality().equals(other.phone, phone) &&
            const DeepCollectionEquality()
                .equals(other.loadingState, loadingState) &&
            const DeepCollectionEquality()
                .equals(other.savingState, savingState));
  }

  @override
  int get hashCode => Object.hash(
      runtimeType,
      const DeepCollectionEquality().hash(name),
      const DeepCollectionEquality().hash(surname),
      const DeepCollectionEquality().hash(patronymic),
      const DeepCollectionEquality().hash(phone),
      const DeepCollectionEquality().hash(loadingState),
      const DeepCollectionEquality().hash(savingState));

  @JsonKey(ignore: true)
  @override
  _$ProfilePageStateCopyWith<_ProfilePageState> get copyWith =>
      __$ProfilePageStateCopyWithImpl<_ProfilePageState>(this, _$identity);
}

abstract class _ProfilePageState implements ProfilePageState {
  const factory _ProfilePageState(
      {String name,
      String surname,
      String patronymic,
      String phone,
      ProgressState loadingState,
      ProgressState savingState}) = _$_ProfilePageState;

  @override
  String get name;
  @override
  String get surname;
  @override
  String get patronymic;
  @override
  String get phone;
  @override
  ProgressState get loadingState;
  @override
  ProgressState get savingState;
  @override
  @JsonKey(ignore: true)
  _$ProfilePageStateCopyWith<_ProfilePageState> get copyWith =>
      throw _privateConstructorUsedError;
}
