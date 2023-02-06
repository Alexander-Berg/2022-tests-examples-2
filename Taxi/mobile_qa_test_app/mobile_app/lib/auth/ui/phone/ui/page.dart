import 'package:flutter_txm_ui_components/components.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../../../../common/broken/providers.dart';

import '../../../../common/validation/models/validation_rules.dart';
import '../../../../utils/localization.dart';
import '../../../../utils/mask_text_controller.dart';
import '../../../../utils/navigation/navigation_manager.dart';
import '../providers.dart';

class PhonePage extends ConsumerWidget {
  const PhonePage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final title = ref.watch(maybeBrokenStringsProvider).phoneTitle(context);

    return TXMScaffold(
      appBar: const TXMScaffoldAppBar(leadingIcon: YXIconData.back),
      header: TXMScaffoldHeaderSliver(title),
      actions: const _PhonePageActions(),
      body: YXListText(
        text: Strings.of(context).phoneBody,
        borderType: YXListBorderType.none,
      ),
    );
  }
}

class _PhonePageActions extends HookConsumerWidget {
  const _PhonePageActions({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final phonePageManager = ref.watch(phonePageStateManager);
    final phone = ref.watch(phonePageStateHolder.select((s) => s.phone));
    final navigator = ref.read(navigationManagerProvider);
    final isValidPhone =
        ref.watch(phoneViewModelProvider.select((s) => s.isValid));

    final phoneMask = RightValidationRules.phoneMask;
    final phoneCode = RightValidationRules.phoneCode;
    final phoneInputController = useMaskTextController(
      mask: phoneMask,
      text: phone.isNotEmpty ? phone : phoneCode,
    );
    final strings = Strings.of(context);

    return TXMScaffoldActions(
      upperItems: [
        YXListInput(
          borderType: YXListBorderType.none,
          placeholderHasDots: false,
          keyboardType: TextInputType.phone,
          hint: strings.phoneInputHint,
          placeholder: strings.phoneInputPlacaholder,
          error: phoneInputController.text == phoneCode || isValidPhone
              ? null
              : strings.wrongFormat,
          controller: phoneInputController,
          maxLength: phoneMask.length,
          onChanged: phonePageManager.onPhoneChanged,
        ),
      ],
      isHorizontal: false,
      primary: YXButton(
        state: isValidPhone ? ButtonState.enabled : ButtonState.disabled,
        onTap: () => phonePageManager.onNextsButtonTapped(),
        title: strings.sendCode,
      ),
      secondary: YXButton(
        onTap: () => navigator.openSupportQuestionsPage(),
        title: strings.askSupport,
      ),
    );
  }
}
