import 'package:flutter_txm_ui_components/components.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

import '../../../../utils/localization.dart';
import '../providers.dart';
import 'views/sign_up_body.dart';

class SignUpPage extends HookConsumerWidget {
  const SignUpPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final pageManager = ref.watch(signUpPageStateManager);
    final isValid = ref.watch(signUpViewModelProvider.select((s) => s.isValid));

    return TXMScaffold(
      appBar: const TXMScaffoldAppBar(leadingIcon: YXIconData.back),
      header: TXMScaffoldHeaderSliver(Strings.of(context).signUpTitle),
      actions: TXMScaffoldActions(
        isRounded: true,
        primary: YXButton(
          onTap: () => pageManager.onNextButtonTapped(),
          state: isValid ? ButtonState.enabled : ButtonState.disabled,
          title: Strings.of(context).next,
        ),
      ),
      body: SignUpBody(
        onNameChanged: pageManager.onNameChanged,
        onPatronymicChanged: pageManager.onPatronymicChanged,
        onSurnameChanged: pageManager.onSurnameChanged,
      ),
    );
  }
}
