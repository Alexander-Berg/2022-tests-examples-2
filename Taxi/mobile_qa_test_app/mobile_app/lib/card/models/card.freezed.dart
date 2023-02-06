// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target

part of 'card.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more informations: https://github.com/rrousselGit/freezed#custom-getters-and-methods');

Card _$CardFromJson(Map<String, dynamic> json) {
  return _Card.fromJson(json);
}

/// @nodoc
class _$CardTearOff {
  const _$CardTearOff();

  _Card call(
      {@JsonKey(name: 'card_number') required String cardNumber,
      @JsonKey(name: 'cvv') required String cvv,
      @JsonKey(name: 'owner') required String owner,
      @JsonKey(name: 'validity_period') required DateTime validityPeriod}) {
    return _Card(
      cardNumber: cardNumber,
      cvv: cvv,
      owner: owner,
      validityPeriod: validityPeriod,
    );
  }

  Card fromJson(Map<String, Object?> json) {
    return Card.fromJson(json);
  }
}

/// @nodoc
const $Card = _$CardTearOff();

/// @nodoc
mixin _$Card {
  @JsonKey(name: 'card_number')
  String get cardNumber => throw _privateConstructorUsedError;
  @JsonKey(name: 'cvv')
  String get cvv => throw _privateConstructorUsedError;
  @JsonKey(name: 'owner')
  String get owner => throw _privateConstructorUsedError;
  @JsonKey(name: 'validity_period')
  DateTime get validityPeriod => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $CardCopyWith<Card> get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $CardCopyWith<$Res> {
  factory $CardCopyWith(Card value, $Res Function(Card) then) =
      _$CardCopyWithImpl<$Res>;
  $Res call(
      {@JsonKey(name: 'card_number') String cardNumber,
      @JsonKey(name: 'cvv') String cvv,
      @JsonKey(name: 'owner') String owner,
      @JsonKey(name: 'validity_period') DateTime validityPeriod});
}

/// @nodoc
class _$CardCopyWithImpl<$Res> implements $CardCopyWith<$Res> {
  _$CardCopyWithImpl(this._value, this._then);

  final Card _value;
  // ignore: unused_field
  final $Res Function(Card) _then;

  @override
  $Res call({
    Object? cardNumber = freezed,
    Object? cvv = freezed,
    Object? owner = freezed,
    Object? validityPeriod = freezed,
  }) {
    return _then(_value.copyWith(
      cardNumber: cardNumber == freezed
          ? _value.cardNumber
          : cardNumber // ignore: cast_nullable_to_non_nullable
              as String,
      cvv: cvv == freezed
          ? _value.cvv
          : cvv // ignore: cast_nullable_to_non_nullable
              as String,
      owner: owner == freezed
          ? _value.owner
          : owner // ignore: cast_nullable_to_non_nullable
              as String,
      validityPeriod: validityPeriod == freezed
          ? _value.validityPeriod
          : validityPeriod // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ));
  }
}

/// @nodoc
abstract class _$CardCopyWith<$Res> implements $CardCopyWith<$Res> {
  factory _$CardCopyWith(_Card value, $Res Function(_Card) then) =
      __$CardCopyWithImpl<$Res>;
  @override
  $Res call(
      {@JsonKey(name: 'card_number') String cardNumber,
      @JsonKey(name: 'cvv') String cvv,
      @JsonKey(name: 'owner') String owner,
      @JsonKey(name: 'validity_period') DateTime validityPeriod});
}

/// @nodoc
class __$CardCopyWithImpl<$Res> extends _$CardCopyWithImpl<$Res>
    implements _$CardCopyWith<$Res> {
  __$CardCopyWithImpl(_Card _value, $Res Function(_Card) _then)
      : super(_value, (v) => _then(v as _Card));

  @override
  _Card get _value => super._value as _Card;

  @override
  $Res call({
    Object? cardNumber = freezed,
    Object? cvv = freezed,
    Object? owner = freezed,
    Object? validityPeriod = freezed,
  }) {
    return _then(_Card(
      cardNumber: cardNumber == freezed
          ? _value.cardNumber
          : cardNumber // ignore: cast_nullable_to_non_nullable
              as String,
      cvv: cvv == freezed
          ? _value.cvv
          : cvv // ignore: cast_nullable_to_non_nullable
              as String,
      owner: owner == freezed
          ? _value.owner
          : owner // ignore: cast_nullable_to_non_nullable
              as String,
      validityPeriod: validityPeriod == freezed
          ? _value.validityPeriod
          : validityPeriod // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$_Card implements _Card {
  const _$_Card(
      {@JsonKey(name: 'card_number') required this.cardNumber,
      @JsonKey(name: 'cvv') required this.cvv,
      @JsonKey(name: 'owner') required this.owner,
      @JsonKey(name: 'validity_period') required this.validityPeriod});

  factory _$_Card.fromJson(Map<String, dynamic> json) => _$$_CardFromJson(json);

  @override
  @JsonKey(name: 'card_number')
  final String cardNumber;
  @override
  @JsonKey(name: 'cvv')
  final String cvv;
  @override
  @JsonKey(name: 'owner')
  final String owner;
  @override
  @JsonKey(name: 'validity_period')
  final DateTime validityPeriod;

  @override
  String toString() {
    return 'Card(cardNumber: $cardNumber, cvv: $cvv, owner: $owner, validityPeriod: $validityPeriod)';
  }

  @override
  bool operator ==(dynamic other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _Card &&
            const DeepCollectionEquality()
                .equals(other.cardNumber, cardNumber) &&
            const DeepCollectionEquality().equals(other.cvv, cvv) &&
            const DeepCollectionEquality().equals(other.owner, owner) &&
            const DeepCollectionEquality()
                .equals(other.validityPeriod, validityPeriod));
  }

  @override
  int get hashCode => Object.hash(
      runtimeType,
      const DeepCollectionEquality().hash(cardNumber),
      const DeepCollectionEquality().hash(cvv),
      const DeepCollectionEquality().hash(owner),
      const DeepCollectionEquality().hash(validityPeriod));

  @JsonKey(ignore: true)
  @override
  _$CardCopyWith<_Card> get copyWith =>
      __$CardCopyWithImpl<_Card>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$_CardToJson(this);
  }
}

abstract class _Card implements Card {
  const factory _Card(
          {@JsonKey(name: 'card_number') required String cardNumber,
          @JsonKey(name: 'cvv') required String cvv,
          @JsonKey(name: 'owner') required String owner,
          @JsonKey(name: 'validity_period') required DateTime validityPeriod}) =
      _$_Card;

  factory _Card.fromJson(Map<String, dynamic> json) = _$_Card.fromJson;

  @override
  @JsonKey(name: 'card_number')
  String get cardNumber;
  @override
  @JsonKey(name: 'cvv')
  String get cvv;
  @override
  @JsonKey(name: 'owner')
  String get owner;
  @override
  @JsonKey(name: 'validity_period')
  DateTime get validityPeriod;
  @override
  @JsonKey(ignore: true)
  _$CardCopyWith<_Card> get copyWith => throw _privateConstructorUsedError;
}
