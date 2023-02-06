// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target

part of 'shop_state.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more informations: https://github.com/rrousselGit/freezed#custom-getters-and-methods');

/// @nodoc
class _$ShopStateTearOff {
  const _$ShopStateTearOff();

  _ShopState call(
      {List<Category> categories = const <Category>[],
      ProgressState status = ProgressState.loading}) {
    return _ShopState(
      categories: categories,
      status: status,
    );
  }
}

/// @nodoc
const $ShopState = _$ShopStateTearOff();

/// @nodoc
mixin _$ShopState {
  List<Category> get categories => throw _privateConstructorUsedError;
  ProgressState get status => throw _privateConstructorUsedError;

  @JsonKey(ignore: true)
  $ShopStateCopyWith<ShopState> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ShopStateCopyWith<$Res> {
  factory $ShopStateCopyWith(ShopState value, $Res Function(ShopState) then) =
      _$ShopStateCopyWithImpl<$Res>;
  $Res call({List<Category> categories, ProgressState status});
}

/// @nodoc
class _$ShopStateCopyWithImpl<$Res> implements $ShopStateCopyWith<$Res> {
  _$ShopStateCopyWithImpl(this._value, this._then);

  final ShopState _value;
  // ignore: unused_field
  final $Res Function(ShopState) _then;

  @override
  $Res call({
    Object? categories = freezed,
    Object? status = freezed,
  }) {
    return _then(_value.copyWith(
      categories: categories == freezed
          ? _value.categories
          : categories // ignore: cast_nullable_to_non_nullable
              as List<Category>,
      status: status == freezed
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as ProgressState,
    ));
  }
}

/// @nodoc
abstract class _$ShopStateCopyWith<$Res> implements $ShopStateCopyWith<$Res> {
  factory _$ShopStateCopyWith(
          _ShopState value, $Res Function(_ShopState) then) =
      __$ShopStateCopyWithImpl<$Res>;
  @override
  $Res call({List<Category> categories, ProgressState status});
}

/// @nodoc
class __$ShopStateCopyWithImpl<$Res> extends _$ShopStateCopyWithImpl<$Res>
    implements _$ShopStateCopyWith<$Res> {
  __$ShopStateCopyWithImpl(_ShopState _value, $Res Function(_ShopState) _then)
      : super(_value, (v) => _then(v as _ShopState));

  @override
  _ShopState get _value => super._value as _ShopState;

  @override
  $Res call({
    Object? categories = freezed,
    Object? status = freezed,
  }) {
    return _then(_ShopState(
      categories: categories == freezed
          ? _value.categories
          : categories // ignore: cast_nullable_to_non_nullable
              as List<Category>,
      status: status == freezed
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as ProgressState,
    ));
  }
}

/// @nodoc

class _$_ShopState implements _ShopState {
  const _$_ShopState(
      {this.categories = const <Category>[],
      this.status = ProgressState.loading});

  @JsonKey()
  @override
  final List<Category> categories;
  @JsonKey()
  @override
  final ProgressState status;

  @override
  String toString() {
    return 'ShopState(categories: $categories, status: $status)';
  }

  @override
  bool operator ==(dynamic other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _ShopState &&
            const DeepCollectionEquality()
                .equals(other.categories, categories) &&
            const DeepCollectionEquality().equals(other.status, status));
  }

  @override
  int get hashCode => Object.hash(
      runtimeType,
      const DeepCollectionEquality().hash(categories),
      const DeepCollectionEquality().hash(status));

  @JsonKey(ignore: true)
  @override
  _$ShopStateCopyWith<_ShopState> get copyWith =>
      __$ShopStateCopyWithImpl<_ShopState>(this, _$identity);
}

abstract class _ShopState implements ShopState {
  const factory _ShopState({List<Category> categories, ProgressState status}) =
      _$_ShopState;

  @override
  List<Category> get categories;
  @override
  ProgressState get status;
  @override
  @JsonKey(ignore: true)
  _$ShopStateCopyWith<_ShopState> get copyWith =>
      throw _privateConstructorUsedError;
}
