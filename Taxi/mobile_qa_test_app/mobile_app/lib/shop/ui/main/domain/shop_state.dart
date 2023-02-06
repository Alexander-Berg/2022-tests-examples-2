import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:models/models.dart';

import '../../../../profile/domain/profile_page_state.dart';

part 'shop_state.freezed.dart';
// part 'shop_state.g.dart';

@freezed
class ShopState with _$ShopState {
  const factory ShopState({
    @Default(<Category>[]) List<Category> categories,
    @Default(ProgressState.loading) ProgressState status,
  }) = _ShopState;
}
