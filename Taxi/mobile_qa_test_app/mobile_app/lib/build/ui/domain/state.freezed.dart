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
class _$BuildPageStateTearOff {
  const _$BuildPageStateTearOff();

  _BuildPageState call(
      {bool isProgress = false,
      String? errorMessage = null,
      String buildCode = ''}) {
    return _BuildPageState(
      isProgress: isProgress,
      errorMessage: errorMessage,
      buildCode: buildCode,
    );
  }
}

/// @nodoc
const $BuildPageState = _$BuildPageStateTearOff();

/// @nodoc
mixin _$BuildPageState {
  bool get isProgress => throw _privateConstructorUsedError;
  String? get errorMessage => throw _privateConstructorUsedError;
  String get buildCode => throw _privateConstructorUsedError;

  @JsonKey(ignore: true)
  $BuildPageStateCopyWith<BuildPageState> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $BuildPageStateCopyWith<$Res> {
  factory $BuildPageStateCopyWith(
          BuildPageState value, $Res Function(BuildPageState) then) =
      _$BuildPageStateCopyWithImpl<$Res>;
  $Res call({bool isProgress, String? errorMessage, String buildCode});
}

/// @nodoc
class _$BuildPageStateCopyWithImpl<$Res>
    implements $BuildPageStateCopyWith<$Res> {
  _$BuildPageStateCopyWithImpl(this._value, this._then);

  final BuildPageState _value;
  // ignore: unused_field
  final $Res Function(BuildPageState) _then;

  @override
  $Res call({
    Object? isProgress = freezed,
    Object? errorMessage = freezed,
    Object? buildCode = freezed,
  }) {
    return _then(_value.copyWith(
      isProgress: isProgress == freezed
          ? _value.isProgress
          : isProgress // ignore: cast_nullable_to_non_nullable
              as bool,
      errorMessage: errorMessage == freezed
          ? _value.errorMessage
          : errorMessage // ignore: cast_nullable_to_non_nullable
              as String?,
      buildCode: buildCode == freezed
          ? _value.buildCode
          : buildCode // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
abstract class _$BuildPageStateCopyWith<$Res>
    implements $BuildPageStateCopyWith<$Res> {
  factory _$BuildPageStateCopyWith(
          _BuildPageState value, $Res Function(_BuildPageState) then) =
      __$BuildPageStateCopyWithImpl<$Res>;
  @override
  $Res call({bool isProgress, String? errorMessage, String buildCode});
}

/// @nodoc
class __$BuildPageStateCopyWithImpl<$Res>
    extends _$BuildPageStateCopyWithImpl<$Res>
    implements _$BuildPageStateCopyWith<$Res> {
  __$BuildPageStateCopyWithImpl(
      _BuildPageState _value, $Res Function(_BuildPageState) _then)
      : super(_value, (v) => _then(v as _BuildPageState));

  @override
  _BuildPageState get _value => super._value as _BuildPageState;

  @override
  $Res call({
    Object? isProgress = freezed,
    Object? errorMessage = freezed,
    Object? buildCode = freezed,
  }) {
    return _then(_BuildPageState(
      isProgress: isProgress == freezed
          ? _value.isProgress
          : isProgress // ignore: cast_nullable_to_non_nullable
              as bool,
      errorMessage: errorMessage == freezed
          ? _value.errorMessage
          : errorMessage // ignore: cast_nullable_to_non_nullable
              as String?,
      buildCode: buildCode == freezed
          ? _value.buildCode
          : buildCode // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc

class _$_BuildPageState implements _BuildPageState {
  _$_BuildPageState(
      {this.isProgress = false, this.errorMessage = null, this.buildCode = ''});

  @JsonKey()
  @override
  final bool isProgress;
  @JsonKey()
  @override
  final String? errorMessage;
  @JsonKey()
  @override
  final String buildCode;

  @override
  String toString() {
    return 'BuildPageState(isProgress: $isProgress, errorMessage: $errorMessage, buildCode: $buildCode)';
  }

  @override
  bool operator ==(dynamic other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _BuildPageState &&
            const DeepCollectionEquality()
                .equals(other.isProgress, isProgress) &&
            const DeepCollectionEquality()
                .equals(other.errorMessage, errorMessage) &&
            const DeepCollectionEquality().equals(other.buildCode, buildCode));
  }

  @override
  int get hashCode => Object.hash(
      runtimeType,
      const DeepCollectionEquality().hash(isProgress),
      const DeepCollectionEquality().hash(errorMessage),
      const DeepCollectionEquality().hash(buildCode));

  @JsonKey(ignore: true)
  @override
  _$BuildPageStateCopyWith<_BuildPageState> get copyWith =>
      __$BuildPageStateCopyWithImpl<_BuildPageState>(this, _$identity);
}

abstract class _BuildPageState implements BuildPageState {
  factory _BuildPageState(
      {bool isProgress,
      String? errorMessage,
      String buildCode}) = _$_BuildPageState;

  @override
  bool get isProgress;
  @override
  String? get errorMessage;
  @override
  String get buildCode;
  @override
  @JsonKey(ignore: true)
  _$BuildPageStateCopyWith<_BuildPageState> get copyWith =>
      throw _privateConstructorUsedError;
}
