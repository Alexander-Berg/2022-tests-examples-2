//ignore_for_file: argument_type_not_assignable
//ignore_for_file: undefined_identifier
//ignore_for_file: non_bool_condition
import 'package:hooks_riverpod/hooks_riverpod.dart';

import '../../providers.dart';
import 'state.dart';

final userPageBrokenStateHolderProvider = StateNotifierProvider.autoDispose<
    UserPageBrokenStateHolder, UserPageBrokenState>(
  (ref) => UserPageBrokenStateHolder(
    UserPageBrokenState(
      shouldBeOnAddTapCrushed:
          ref.watch(isBrokenProvider(BugKeys.userPageFreezeOnAddTap)),
      shouldBeOnInitCrushed:
          ref.watch(isBrokenProvider(BugKeys.userPageCrushOnInit)),
    ),
  ),
);

/// Данный класс отличается по названию от state holder для страницы
/// и отвечает за состояния краша самой страницы
class UserPageBrokenStateHolder extends StateNotifier<UserPageBrokenState> {
  UserPageBrokenStateHolder([UserPageBrokenState? state])
      : super(state ?? UserPageBrokenState());

  void crush() {
    state = UserPageBrokenState(brokenType: BrokenType.crushed);
  }
}
