import 'package:flutter_txm_ui_components/components.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

import '../l10n/app_localizations.dart';
import 'localization.dart';
import 'navigation/navigation_state_holder.dart';

final toasterManagerProvider = Provider((ref) {
  final navitatorState = ref.watch(navigationKeyProvider).currentState;

  return ToasterManager(navitatorState);
});

class ToasterManager {
  final NavigatorState? navigatorState;
  ToasterManager(this.navigatorState);

  void _showToast({
    required String message,
    IconData? icon,
    Color? iconColor,
  }) {
    final context = navigatorState?.context;
    final overlay = navigatorState?.overlay;
    if (context == null || overlay == null) {
      return;
    }
    TXMToast.show(
      context,
      overlayState: overlay,
      leading: YXTip(
        icon: icon,
        color: iconColor,
      ),
      body: YXListText(
        text: message,
        borderType: YXListBorderType.none,
        type: YXListTextType.marginNone,
      ),
    );
  }

  //ignore: avoid-non-null-assertion
  AppLocalizations get _strings => Strings.of(navigatorState!.context);

  void showErrorMessage(String message) => _showToast(
        icon: YXIconData.warning,
        message: message,
        iconColor: YXColors.redToxic,
      );

  void showErrorUserNotFound() {
    _showToast(
      icon: YXIconData.warning,
      message: _strings.userNotFound,
    );
  }

  void showDoneMessage(String message) {
    _showToast(
      icon: YXIconData.check,
      message: message,
      iconColor: YXColors.greenNormal,
    );
  }

  void showProfileDeletedMessage() {
    showDoneMessage(_strings.profileDeleted);
  }

  void showUnknowedError() {
    showErrorMessage(_strings.unknowedError);
  }

  void showSavedMessage() {
    showDoneMessage(_strings.saved);
  }
}
