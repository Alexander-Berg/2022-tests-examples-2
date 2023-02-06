//ignore_for_file: argument_type_not_assignable
//ignore_for_file: undefined_identifier
//ignore_for_file: non_bool_condition
import 'package:hooks_riverpod/hooks_riverpod.dart';

import '../../providers.dart';
import 'state_holder.dart';

final userPageManagerProvider = Provider((ref) {
  if (ref.watch(isBrokenProvider(BugKeys.userPageCrushOnInit)) ||
      ref.watch(isBrokenProvider(BugKeys.userPageFreezeOnAddTap))) {
    return BrokenUserPageManager(
      ref.read(userPageBrokenStateHolderProvider.notifier),
    );
  }

  return UserPageManager();
});

/// Данный стэйт холдер будет отвечать как за сломанное поведение
/// бизнес логики, так и за краш всей страницы. Хотя возможно стоит
/// краш страницы вынести в отдельный менеджер, потому что стэйт я
/// разделил
class BrokenUserPageManager extends UserPageManager {
  UserPageBrokenStateHolder brokenState;

  BrokenUserPageManager(this.brokenState);

  @override
  void onInit() {
    if (brokenState.state.shouldBeOnInitCrushed) {
      brokenState.crush();
    }
    super.onInit();
  }

  @override
  void onAddTap() {
    if (brokenState.state.shouldBeOnAddTapCrushed) {
      brokenState.crush();
    } else {
      super.onAddTap();
    }
  }
}

class UserPageManager {
  void onAddTap() {}

  void onInit() {}
}
