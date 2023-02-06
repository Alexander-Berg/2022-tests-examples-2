import 'package:flutter_txm_ui_components/components.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

import '../../../../common/validation/models/validation_rules.dart';
import '../../../../utils/localization.dart';
import '../../../../utils/mask_text_controller.dart';
import '../../../../utils/navigation/navigation_manager.dart';
import '../providers.dart';

class CodePage extends ConsumerWidget {
  const CodePage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) => TXMScaffold(
        appBar: const TXMScaffoldAppBar(leadingIcon: YXIconData.back),
        header: TXMScaffoldHeaderSliver(Strings.of(context).codeTitle),
        actions: const _CodePageActions(),
        body: YXListText(
          text: Strings.of(context).codeBody,
          borderType: YXListBorderType.none,
        ),
      );
}

class _CodePageActions extends HookConsumerWidget {
  const _CodePageActions({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isValidCode =
        ref.watch(codeViewModelProvider.select((s) => s.isValid));
    final codePageManager = ref.watch(codePageStateManager);
    final navigator = ref.read(navigationManagerProvider);
    final codeController = useMaskTextController(
      mask: RightValidationRules.smsCodeMask,
    );

    return TXMScaffoldActions(
      isHorizontal: false,
      primary: YXButton(
        onTap: () => codePageManager.onNextButtonTapped(),
        title: Strings.of(context).submit,
        state: isValidCode ? ButtonState.enabled : ButtonState.disabled,
      ),
      secondary: YXButton(
        onTap: () => navigator.openSupportQuestionsPage(),
        title: Strings.of(context).askSupport,
      ),
      upperItems: [
        YXListInput(
          controller: codeController,
          useHintAsPlaceholder: true,
          borderType: YXListBorderType.bottom,
          hint: Strings.of(context).codeInputHint,
          keyboardType: TextInputType.number,
          maxLength: 5,
          onChanged: codePageManager.onCodeChanged,
        ),
      ],
    );
  }
}
