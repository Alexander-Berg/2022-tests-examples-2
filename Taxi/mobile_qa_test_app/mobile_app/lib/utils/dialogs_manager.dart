import 'package:flutter_txm_ui_components/components.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

import '../l10n/app_localizations.dart';
import 'localization.dart';
import 'navigation/navigation_state_holder.dart';

final dialogsManagerProvider = Provider((ref) => DialogsManager(
      navigatorState: ref.watch(navigationKeyProvider).currentState,
    ));

class DialogsManager {
  final NavigatorState? navigatorState;
  DialogsManager({
    this.navigatorState,
  });

  //ignore: avoid-non-null-assertion
  AppLocalizations get _strings => Strings.of(navigatorState!.context);

  Future<void> showDialog({
    required String title,
    required TXMAction primaryAction,
    String? text,
    TXMAction? secondaryAction,
  }) async {
    final context = navigatorState?.context;
    if (context == null) {
      return;
    }

    return TXMDialog.show(
      context,
      title: title,
      text: text,
      primaryAction: primaryAction,
      secondaryAction: secondaryAction,
    );
  }

  Future<bool> showConfirm({
    required String title,
    String? text,
  }) async {
    var result = false;

    await showDialog(
      title: title,
      text: text,
      primaryAction: TXMAction(
        text: _strings.yes,
        callback: () {
          result = true;
        },
      ),
      secondaryAction: TXMAction(
        text: _strings.no,
      ),
    );

    return result;
  }

  Future<bool> showConfirmAccountDeletion() => showConfirm(
        title: _strings.areYouSureYouWantDeleteAccount,
        text: _strings.deleteAccountAttention,
      );
}
