// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target

part of 'state.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more informations: https://github.com/rrousselGit/freezed#custom-getters-and-methods');

/// @nodoc
class _$PaymentPageStateTearOff {
  const _$PaymentPageStateTearOff();

  _PaymentPageState call(
      {PaymentOption selected = PaymentOption.cash,
      bool isLoading = false,
      List<PaymentOption> enabledOptions = const [PaymentOption.cash]}) {
    return _PaymentPageState(
      selected: selected,
      isLoading: isLoading,
      enabledOptions: enabledOptions,
    );
  }
}

/// @nodoc
const $PaymentPageState = _$PaymentPageStateTearOff();

/// @nodoc
mixin _$PaymentPageState {
  PaymentOption get selected => throw _privateConstructorUsedError;
  bool get isLoading => throw _privateConstructorUsedError;
  List<PaymentOption> get enabledOptions => throw _privateConstructorUsedError;

  @JsonKey(ignore: true)
  $PaymentPageStateCopyWith<PaymentPageState> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $PaymentPageStateCopyWith<$Res> {
  factory $PaymentPageStateCopyWith(
          PaymentPageState value, $Res Function(PaymentPageState) then) =
      _$PaymentPageStateCopyWithImpl<$Res>;
  $Res call(
      {PaymentOption selected,
      bool isLoading,
      List<PaymentOption> enabledOptions});
}

/// @nodoc
class _$PaymentPageStateCopyWithImpl<$Res>
    implements $PaymentPageStateCopyWith<$Res> {
  _$PaymentPageStateCopyWithImpl(this._value, this._then);

  final PaymentPageState _value;
  // ignore: unused_field
  final $Res Function(PaymentPageState) _then;

  @override
  $Res call({
    Object? selected = freezed,
    Object? isLoading = freezed,
    Object? enabledOptions = freezed,
  }) {
    return _then(_value.copyWith(
      selected: selected == freezed
          ? _value.selected
          : selected // ignore: cast_nullable_to_non_nullable
              as PaymentOption,
      isLoading: isLoading == freezed
          ? _value.isLoading
          : isLoading // ignore: cast_nullable_to_non_nullable
              as bool,
      enabledOptions: enabledOptions == freezed
          ? _value.enabledOptions
          : enabledOptions // ignore: cast_nullable_to_non_nullable
              as List<PaymentOption>,
    ));
  }
}

/// @nodoc
abstract class _$PaymentPageStateCopyWith<$Res>
    implements $PaymentPageStateCopyWith<$Res> {
  factory _$PaymentPageStateCopyWith(
          _PaymentPageState value, $Res Function(_PaymentPageState) then) =
      __$PaymentPageStateCopyWithImpl<$Res>;
  @override
  $Res call(
      {PaymentOption selected,
      bool isLoading,
      List<PaymentOption> enabledOptions});
}

/// @nodoc
class __$PaymentPageStateCopyWithImpl<$Res>
    extends _$PaymentPageStateCopyWithImpl<$Res>
    implements _$PaymentPageStateCopyWith<$Res> {
  __$PaymentPageStateCopyWithImpl(
      _PaymentPageState _value, $Res Function(_PaymentPageState) _then)
      : super(_value, (v) => _then(v as _PaymentPageState));

  @override
  _PaymentPageState get _value => super._value as _PaymentPageState;

  @override
  $Res call({
    Object? selected = freezed,
    Object? isLoading = freezed,
    Object? enabledOptions = freezed,
  }) {
    return _then(_PaymentPageState(
      selected: selected == freezed
          ? _value.selected
          : selected // ignore: cast_nullable_to_non_nullable
              as PaymentOption,
      isLoading: isLoading == freezed
          ? _value.isLoading
          : isLoading // ignore: cast_nullable_to_non_nullable
              as bool,
      enabledOptions: enabledOptions == freezed
          ? _value.enabledOptions
          : enabledOptions // ignore: cast_nullable_to_non_nullable
              as List<PaymentOption>,
    ));
  }
}

/// @nodoc

class _$_PaymentPageState implements _PaymentPageState {
  _$_PaymentPageState(
      {this.selected = PaymentOption.cash,
      this.isLoading = false,
      this.enabledOptions = const [PaymentOption.cash]});

  @JsonKey()
  @override
  final PaymentOption selected;
  @JsonKey()
  @override
  final bool isLoading;
  @JsonKey()
  @override
  final List<PaymentOption> enabledOptions;

  @override
  String toString() {
    return 'PaymentPageState(selected: $selected, isLoading: $isLoading, enabledOptions: $enabledOptions)';
  }

  @override
  bool operator ==(dynamic other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _PaymentPageState &&
            const DeepCollectionEquality().equals(other.selected, selected) &&
            const DeepCollectionEquality().equals(other.isLoading, isLoading) &&
            const DeepCollectionEquality()
                .equals(other.enabledOptions, enabledOptions));
  }

  @override
  int get hashCode => Object.hash(
      runtimeType,
      const DeepCollectionEquality().hash(selected),
      const DeepCollectionEquality().hash(isLoading),
      const DeepCollectionEquality().hash(enabledOptions));

  @JsonKey(ignore: true)
  @override
  _$PaymentPageStateCopyWith<_PaymentPageState> get copyWith =>
      __$PaymentPageStateCopyWithImpl<_PaymentPageState>(this, _$identity);
}

abstract class _PaymentPageState implements PaymentPageState {
  factory _PaymentPageState(
      {PaymentOption selected,
      bool isLoading,
      List<PaymentOption> enabledOptions}) = _$_PaymentPageState;

  @override
  PaymentOption get selected;
  @override
  bool get isLoading;
  @override
  List<PaymentOption> get enabledOptions;
  @override
  @JsonKey(ignore: true)
  _$PaymentPageStateCopyWith<_PaymentPageState> get copyWith =>
      throw _privateConstructorUsedError;
}
