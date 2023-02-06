import 'package:flutter_txm_ui_components/components.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

import '../../../utils/localization.dart';
import '../../../utils/navigation/navigation_manager.dart';
import '../../domain/profile_page_state.dart';
import '../../providers.dart';
import '../profile_view_model.dart';

class ProfilePageActions extends ConsumerWidget {
  const ProfilePageActions({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final profileManager = ref.watch(profilePageStateManager);
    final savingState =
        ref.watch(profilePageStateHolder.select((s) => s.savingState));
    final navigator = ref.watch(navigationManagerProvider);
    final isValid = ref.watch(profileViewModel.select((v) => v.isValid));

    return TXMScaffoldActions(
      isHorizontal: false,
      mode: TXMScaffoldActionsMode.overflow,
      isRounded: true,
      primary: YXButton(
        state: _saveButtonState(isValid, savingState),
        title: Strings.of(context).saveChanges,
        onTap: () => profileManager.onSaveChangesTapped(),
      ),
      secondary: YXButton(
        title: Strings.of(context).askSupport,
        onTap: () => navigator.openSupportQuestionsPage(),
      ),
    );
  }

  ButtonState _saveButtonState(bool isValid, ProgressState savingState) {
    if (savingState == ProgressState.loading) {
      return ButtonState.loading;
    }
    if (isValid) {
      return ButtonState.enabled;
    }

    return ButtonState.disabled;
  }
}
