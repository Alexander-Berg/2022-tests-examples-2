// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target

part of 'address_page_state.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more informations: https://github.com/rrousselGit/freezed#custom-getters-and-methods');

AddressPageState _$AddressPageStateFromJson(Map<String, dynamic> json) {
  return _AddressPageState.fromJson(json);
}

/// @nodoc
class _$AddressPageStateTearOff {
  const _$AddressPageStateTearOff();

  _AddressPageState call(
      {String? city,
      String? street,
      String? house,
      String? corpus,
      String? building}) {
    return _AddressPageState(
      city: city,
      street: street,
      house: house,
      corpus: corpus,
      building: building,
    );
  }

  AddressPageState fromJson(Map<String, Object?> json) {
    return AddressPageState.fromJson(json);
  }
}

/// @nodoc
const $AddressPageState = _$AddressPageStateTearOff();

/// @nodoc
mixin _$AddressPageState {
  String? get city => throw _privateConstructorUsedError;
  String? get street => throw _privateConstructorUsedError;
  String? get house => throw _privateConstructorUsedError;
  String? get corpus => throw _privateConstructorUsedError;
  String? get building => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $AddressPageStateCopyWith<AddressPageState> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $AddressPageStateCopyWith<$Res> {
  factory $AddressPageStateCopyWith(
          AddressPageState value, $Res Function(AddressPageState) then) =
      _$AddressPageStateCopyWithImpl<$Res>;
  $Res call(
      {String? city,
      String? street,
      String? house,
      String? corpus,
      String? building});
}

/// @nodoc
class _$AddressPageStateCopyWithImpl<$Res>
    implements $AddressPageStateCopyWith<$Res> {
  _$AddressPageStateCopyWithImpl(this._value, this._then);

  final AddressPageState _value;
  // ignore: unused_field
  final $Res Function(AddressPageState) _then;

  @override
  $Res call({
    Object? city = freezed,
    Object? street = freezed,
    Object? house = freezed,
    Object? corpus = freezed,
    Object? building = freezed,
  }) {
    return _then(_value.copyWith(
      city: city == freezed
          ? _value.city
          : city // ignore: cast_nullable_to_non_nullable
              as String?,
      street: street == freezed
          ? _value.street
          : street // ignore: cast_nullable_to_non_nullable
              as String?,
      house: house == freezed
          ? _value.house
          : house // ignore: cast_nullable_to_non_nullable
              as String?,
      corpus: corpus == freezed
          ? _value.corpus
          : corpus // ignore: cast_nullable_to_non_nullable
              as String?,
      building: building == freezed
          ? _value.building
          : building // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
abstract class _$AddressPageStateCopyWith<$Res>
    implements $AddressPageStateCopyWith<$Res> {
  factory _$AddressPageStateCopyWith(
          _AddressPageState value, $Res Function(_AddressPageState) then) =
      __$AddressPageStateCopyWithImpl<$Res>;
  @override
  $Res call(
      {String? city,
      String? street,
      String? house,
      String? corpus,
      String? building});
}

/// @nodoc
class __$AddressPageStateCopyWithImpl<$Res>
    extends _$AddressPageStateCopyWithImpl<$Res>
    implements _$AddressPageStateCopyWith<$Res> {
  __$AddressPageStateCopyWithImpl(
      _AddressPageState _value, $Res Function(_AddressPageState) _then)
      : super(_value, (v) => _then(v as _AddressPageState));

  @override
  _AddressPageState get _value => super._value as _AddressPageState;

  @override
  $Res call({
    Object? city = freezed,
    Object? street = freezed,
    Object? house = freezed,
    Object? corpus = freezed,
    Object? building = freezed,
  }) {
    return _then(_AddressPageState(
      city: city == freezed
          ? _value.city
          : city // ignore: cast_nullable_to_non_nullable
              as String?,
      street: street == freezed
          ? _value.street
          : street // ignore: cast_nullable_to_non_nullable
              as String?,
      house: house == freezed
          ? _value.house
          : house // ignore: cast_nullable_to_non_nullable
              as String?,
      corpus: corpus == freezed
          ? _value.corpus
          : corpus // ignore: cast_nullable_to_non_nullable
              as String?,
      building: building == freezed
          ? _value.building
          : building // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$_AddressPageState implements _AddressPageState {
  const _$_AddressPageState(
      {this.city, this.street, this.house, this.corpus, this.building});

  factory _$_AddressPageState.fromJson(Map<String, dynamic> json) =>
      _$$_AddressPageStateFromJson(json);

  @override
  final String? city;
  @override
  final String? street;
  @override
  final String? house;
  @override
  final String? corpus;
  @override
  final String? building;

  @override
  String toString() {
    return 'AddressPageState(city: $city, street: $street, house: $house, corpus: $corpus, building: $building)';
  }

  @override
  bool operator ==(dynamic other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _AddressPageState &&
            const DeepCollectionEquality().equals(other.city, city) &&
            const DeepCollectionEquality().equals(other.street, street) &&
            const DeepCollectionEquality().equals(other.house, house) &&
            const DeepCollectionEquality().equals(other.corpus, corpus) &&
            const DeepCollectionEquality().equals(other.building, building));
  }

  @override
  int get hashCode => Object.hash(
      runtimeType,
      const DeepCollectionEquality().hash(city),
      const DeepCollectionEquality().hash(street),
      const DeepCollectionEquality().hash(house),
      const DeepCollectionEquality().hash(corpus),
      const DeepCollectionEquality().hash(building));

  @JsonKey(ignore: true)
  @override
  _$AddressPageStateCopyWith<_AddressPageState> get copyWith =>
      __$AddressPageStateCopyWithImpl<_AddressPageState>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$_AddressPageStateToJson(this);
  }
}

abstract class _AddressPageState implements AddressPageState {
  const factory _AddressPageState(
      {String? city,
      String? street,
      String? house,
      String? corpus,
      String? building}) = _$_AddressPageState;

  factory _AddressPageState.fromJson(Map<String, dynamic> json) =
      _$_AddressPageState.fromJson;

  @override
  String? get city;
  @override
  String? get street;
  @override
  String? get house;
  @override
  String? get corpus;
  @override
  String? get building;
  @override
  @JsonKey(ignore: true)
  _$AddressPageStateCopyWith<_AddressPageState> get copyWith =>
      throw _privateConstructorUsedError;
}
