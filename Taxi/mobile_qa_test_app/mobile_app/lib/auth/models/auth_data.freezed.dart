// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target

part of 'auth_data.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more informations: https://github.com/rrousselGit/freezed#custom-getters-and-methods');

AuthData _$AuthDataFromJson(Map<String, dynamic> json) {
  switch (json['runtimeType']) {
    case 'signIn':
      return AuthDataSignIn.fromJson(json);
    case 'signUp':
      return AuthDataSignUp.fromJson(json);

    default:
      throw CheckedFromJsonException(json, 'runtimeType', 'AuthData',
          'Invalid union type "${json['runtimeType']}"!');
  }
}

/// @nodoc
class _$AuthDataTearOff {
  const _$AuthDataTearOff();

  AuthDataSignIn signIn({String? phone}) {
    return AuthDataSignIn(
      phone: phone,
    );
  }

  AuthDataSignUp signUp(
      {String? phone, String? name, String? surname, String? patronymic}) {
    return AuthDataSignUp(
      phone: phone,
      name: name,
      surname: surname,
      patronymic: patronymic,
    );
  }

  AuthData fromJson(Map<String, Object?> json) {
    return AuthData.fromJson(json);
  }
}

/// @nodoc
const $AuthData = _$AuthDataTearOff();

/// @nodoc
mixin _$AuthData {
  String? get phone => throw _privateConstructorUsedError;

  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function(String? phone) signIn,
    required TResult Function(
            String? phone, String? name, String? surname, String? patronymic)
        signUp,
  }) =>
      throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult Function(String? phone)? signIn,
    TResult Function(
            String? phone, String? name, String? surname, String? patronymic)?
        signUp,
  }) =>
      throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function(String? phone)? signIn,
    TResult Function(
            String? phone, String? name, String? surname, String? patronymic)?
        signUp,
    required TResult orElse(),
  }) =>
      throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult map<TResult extends Object?>({
    required TResult Function(AuthDataSignIn value) signIn,
    required TResult Function(AuthDataSignUp value) signUp,
  }) =>
      throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>({
    TResult Function(AuthDataSignIn value)? signIn,
    TResult Function(AuthDataSignUp value)? signUp,
  }) =>
      throw _privateConstructorUsedError;
  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>({
    TResult Function(AuthDataSignIn value)? signIn,
    TResult Function(AuthDataSignUp value)? signUp,
    required TResult orElse(),
  }) =>
      throw _privateConstructorUsedError;
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $AuthDataCopyWith<AuthData> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $AuthDataCopyWith<$Res> {
  factory $AuthDataCopyWith(AuthData value, $Res Function(AuthData) then) =
      _$AuthDataCopyWithImpl<$Res>;
  $Res call({String? phone});
}

/// @nodoc
class _$AuthDataCopyWithImpl<$Res> implements $AuthDataCopyWith<$Res> {
  _$AuthDataCopyWithImpl(this._value, this._then);

  final AuthData _value;
  // ignore: unused_field
  final $Res Function(AuthData) _then;

  @override
  $Res call({
    Object? phone = freezed,
  }) {
    return _then(_value.copyWith(
      phone: phone == freezed
          ? _value.phone
          : phone // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
abstract class $AuthDataSignInCopyWith<$Res>
    implements $AuthDataCopyWith<$Res> {
  factory $AuthDataSignInCopyWith(
          AuthDataSignIn value, $Res Function(AuthDataSignIn) then) =
      _$AuthDataSignInCopyWithImpl<$Res>;
  @override
  $Res call({String? phone});
}

/// @nodoc
class _$AuthDataSignInCopyWithImpl<$Res> extends _$AuthDataCopyWithImpl<$Res>
    implements $AuthDataSignInCopyWith<$Res> {
  _$AuthDataSignInCopyWithImpl(
      AuthDataSignIn _value, $Res Function(AuthDataSignIn) _then)
      : super(_value, (v) => _then(v as AuthDataSignIn));

  @override
  AuthDataSignIn get _value => super._value as AuthDataSignIn;

  @override
  $Res call({
    Object? phone = freezed,
  }) {
    return _then(AuthDataSignIn(
      phone: phone == freezed
          ? _value.phone
          : phone // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$AuthDataSignIn with DiagnosticableTreeMixin implements AuthDataSignIn {
  const _$AuthDataSignIn({this.phone, String? $type})
      : $type = $type ?? 'signIn';

  factory _$AuthDataSignIn.fromJson(Map<String, dynamic> json) =>
      _$$AuthDataSignInFromJson(json);

  @override
  final String? phone;

  @JsonKey(name: 'runtimeType')
  final String $type;

  @override
  String toString({DiagnosticLevel minLevel = DiagnosticLevel.info}) {
    return 'AuthData.signIn(phone: $phone)';
  }

  @override
  void debugFillProperties(DiagnosticPropertiesBuilder properties) {
    super.debugFillProperties(properties);
    properties
      ..add(DiagnosticsProperty('type', 'AuthData.signIn'))
      ..add(DiagnosticsProperty('phone', phone));
  }

  @override
  bool operator ==(dynamic other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is AuthDataSignIn &&
            const DeepCollectionEquality().equals(other.phone, phone));
  }

  @override
  int get hashCode =>
      Object.hash(runtimeType, const DeepCollectionEquality().hash(phone));

  @JsonKey(ignore: true)
  @override
  $AuthDataSignInCopyWith<AuthDataSignIn> get copyWith =>
      _$AuthDataSignInCopyWithImpl<AuthDataSignIn>(this, _$identity);

  @override
  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function(String? phone) signIn,
    required TResult Function(
            String? phone, String? name, String? surname, String? patronymic)
        signUp,
  }) {
    return signIn(phone);
  }

  @override
  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult Function(String? phone)? signIn,
    TResult Function(
            String? phone, String? name, String? surname, String? patronymic)?
        signUp,
  }) {
    return signIn?.call(phone);
  }

  @override
  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function(String? phone)? signIn,
    TResult Function(
            String? phone, String? name, String? surname, String? patronymic)?
        signUp,
    required TResult orElse(),
  }) {
    if (signIn != null) {
      return signIn(phone);
    }
    return orElse();
  }

  @override
  @optionalTypeArgs
  TResult map<TResult extends Object?>({
    required TResult Function(AuthDataSignIn value) signIn,
    required TResult Function(AuthDataSignUp value) signUp,
  }) {
    return signIn(this);
  }

  @override
  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>({
    TResult Function(AuthDataSignIn value)? signIn,
    TResult Function(AuthDataSignUp value)? signUp,
  }) {
    return signIn?.call(this);
  }

  @override
  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>({
    TResult Function(AuthDataSignIn value)? signIn,
    TResult Function(AuthDataSignUp value)? signUp,
    required TResult orElse(),
  }) {
    if (signIn != null) {
      return signIn(this);
    }
    return orElse();
  }

  @override
  Map<String, dynamic> toJson() {
    return _$$AuthDataSignInToJson(this);
  }
}

abstract class AuthDataSignIn implements AuthData {
  const factory AuthDataSignIn({String? phone}) = _$AuthDataSignIn;

  factory AuthDataSignIn.fromJson(Map<String, dynamic> json) =
      _$AuthDataSignIn.fromJson;

  @override
  String? get phone;
  @override
  @JsonKey(ignore: true)
  $AuthDataSignInCopyWith<AuthDataSignIn> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $AuthDataSignUpCopyWith<$Res>
    implements $AuthDataCopyWith<$Res> {
  factory $AuthDataSignUpCopyWith(
          AuthDataSignUp value, $Res Function(AuthDataSignUp) then) =
      _$AuthDataSignUpCopyWithImpl<$Res>;
  @override
  $Res call({String? phone, String? name, String? surname, String? patronymic});
}

/// @nodoc
class _$AuthDataSignUpCopyWithImpl<$Res> extends _$AuthDataCopyWithImpl<$Res>
    implements $AuthDataSignUpCopyWith<$Res> {
  _$AuthDataSignUpCopyWithImpl(
      AuthDataSignUp _value, $Res Function(AuthDataSignUp) _then)
      : super(_value, (v) => _then(v as AuthDataSignUp));

  @override
  AuthDataSignUp get _value => super._value as AuthDataSignUp;

  @override
  $Res call({
    Object? phone = freezed,
    Object? name = freezed,
    Object? surname = freezed,
    Object? patronymic = freezed,
  }) {
    return _then(AuthDataSignUp(
      phone: phone == freezed
          ? _value.phone
          : phone // ignore: cast_nullable_to_non_nullable
              as String?,
      name: name == freezed
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String?,
      surname: surname == freezed
          ? _value.surname
          : surname // ignore: cast_nullable_to_non_nullable
              as String?,
      patronymic: patronymic == freezed
          ? _value.patronymic
          : patronymic // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$AuthDataSignUp with DiagnosticableTreeMixin implements AuthDataSignUp {
  const _$AuthDataSignUp(
      {this.phone, this.name, this.surname, this.patronymic, String? $type})
      : $type = $type ?? 'signUp';

  factory _$AuthDataSignUp.fromJson(Map<String, dynamic> json) =>
      _$$AuthDataSignUpFromJson(json);

  @override
  final String? phone;
  @override
  final String? name;
  @override
  final String? surname;
  @override
  final String? patronymic;

  @JsonKey(name: 'runtimeType')
  final String $type;

  @override
  String toString({DiagnosticLevel minLevel = DiagnosticLevel.info}) {
    return 'AuthData.signUp(phone: $phone, name: $name, surname: $surname, patronymic: $patronymic)';
  }

  @override
  void debugFillProperties(DiagnosticPropertiesBuilder properties) {
    super.debugFillProperties(properties);
    properties
      ..add(DiagnosticsProperty('type', 'AuthData.signUp'))
      ..add(DiagnosticsProperty('phone', phone))
      ..add(DiagnosticsProperty('name', name))
      ..add(DiagnosticsProperty('surname', surname))
      ..add(DiagnosticsProperty('patronymic', patronymic));
  }

  @override
  bool operator ==(dynamic other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is AuthDataSignUp &&
            const DeepCollectionEquality().equals(other.phone, phone) &&
            const DeepCollectionEquality().equals(other.name, name) &&
            const DeepCollectionEquality().equals(other.surname, surname) &&
            const DeepCollectionEquality()
                .equals(other.patronymic, patronymic));
  }

  @override
  int get hashCode => Object.hash(
      runtimeType,
      const DeepCollectionEquality().hash(phone),
      const DeepCollectionEquality().hash(name),
      const DeepCollectionEquality().hash(surname),
      const DeepCollectionEquality().hash(patronymic));

  @JsonKey(ignore: true)
  @override
  $AuthDataSignUpCopyWith<AuthDataSignUp> get copyWith =>
      _$AuthDataSignUpCopyWithImpl<AuthDataSignUp>(this, _$identity);

  @override
  @optionalTypeArgs
  TResult when<TResult extends Object?>({
    required TResult Function(String? phone) signIn,
    required TResult Function(
            String? phone, String? name, String? surname, String? patronymic)
        signUp,
  }) {
    return signUp(phone, name, surname, patronymic);
  }

  @override
  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>({
    TResult Function(String? phone)? signIn,
    TResult Function(
            String? phone, String? name, String? surname, String? patronymic)?
        signUp,
  }) {
    return signUp?.call(phone, name, surname, patronymic);
  }

  @override
  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>({
    TResult Function(String? phone)? signIn,
    TResult Function(
            String? phone, String? name, String? surname, String? patronymic)?
        signUp,
    required TResult orElse(),
  }) {
    if (signUp != null) {
      return signUp(phone, name, surname, patronymic);
    }
    return orElse();
  }

  @override
  @optionalTypeArgs
  TResult map<TResult extends Object?>({
    required TResult Function(AuthDataSignIn value) signIn,
    required TResult Function(AuthDataSignUp value) signUp,
  }) {
    return signUp(this);
  }

  @override
  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>({
    TResult Function(AuthDataSignIn value)? signIn,
    TResult Function(AuthDataSignUp value)? signUp,
  }) {
    return signUp?.call(this);
  }

  @override
  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>({
    TResult Function(AuthDataSignIn value)? signIn,
    TResult Function(AuthDataSignUp value)? signUp,
    required TResult orElse(),
  }) {
    if (signUp != null) {
      return signUp(this);
    }
    return orElse();
  }

  @override
  Map<String, dynamic> toJson() {
    return _$$AuthDataSignUpToJson(this);
  }
}

abstract class AuthDataSignUp implements AuthData {
  const factory AuthDataSignUp(
      {String? phone,
      String? name,
      String? surname,
      String? patronymic}) = _$AuthDataSignUp;

  factory AuthDataSignUp.fromJson(Map<String, dynamic> json) =
      _$AuthDataSignUp.fromJson;

  @override
  String? get phone;
  String? get name;
  String? get surname;
  String? get patronymic;
  @override
  @JsonKey(ignore: true)
  $AuthDataSignUpCopyWith<AuthDataSignUp> get copyWith =>
      throw _privateConstructorUsedError;
}
