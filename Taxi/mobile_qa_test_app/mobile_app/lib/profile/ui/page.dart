import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:flutter_txm_ui_components/components.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

import '../../app_loader/ui/loading_page.dart';
import '../../auth/providers.dart';
import '../../common/validation/models/validation_rules.dart';
import '../../configs/app_state.dart';
import '../../configs/configs_providers.dart';
import '../../utils/localization.dart';
// import '../../utils/mask_text_controller.dart';
import '../../utils/mask_text_controller.dart';
import '../../utils/navigation/navigation_manager.dart';
import '../domain/profile_page_state.dart';
import '../providers.dart';
import 'components/profile_page_actions.dart';

class ProfilePage extends HookConsumerWidget {
  const ProfilePage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    useEffect(
      () {
        ref.read(profilePageStateManager).init();
      },
      const [],
    );
    final authManager = ref.watch(authManagerProvider);
    final loadingState = ref.watch(profilePageStateHolder.select(
      (s) => s.loadingState,
    ));

    return loadingState == ProgressState.loading
        ? const AppLoadingPage()
        : TXMScaffold(
            appBar: TXMScaffoldAppBar(
              leadingIcon: YXIconData.back,
              actions: [
                YXButton(
                  title: Strings.of(context).exit,
                  onTap: () => authManager.onSignOutClicked(),
                ),
              ],
            ),
            header: TXMScaffoldHeaderSliver(Strings.of(context).profile),
            body: _ProfileBody(),
            actions: const ProfilePageActions(),
          );
  }
}

class _ProfileBody extends HookConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final navigator = ref.watch(navigationManagerProvider);
    final profileManager = ref.watch(profilePageStateManager);
    final isDarkTheme = ref.watch(appStateProvider.select((s) => s.isDark));
    final themeManager = ref.watch(appManagerProvider);
    final phoneMask = RightValidationRules.phoneMask;
    final phoneCode = RightValidationRules.phoneCode;
    final profileState = ref.watch(profilePageStateHolder);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        ProfileInput(
          placeholder: Strings.of(context).surnameInputHint,
          initialText: profileState.surname,
          onChanged: (val) => profileManager.onSurnameChanged(val ?? ''),
        ),
        ProfileInput(
          placeholder: Strings.of(context).nameInputHint,
          initialText: profileState.name,
          onChanged: (val) => profileManager.onNameChanged(val ?? ''),
        ),
        ProfileInput(
          placeholder: Strings.of(context).patronymicInputHint,
          initialText: profileState.patronymic,
          onChanged: (val) => profileManager.onPatronymicChanged(val ?? ''),
        ),
        ProfileInput(
          mask: phoneMask,
          initialText:
              profileState.phone.isNotEmpty ? profileState.phone : phoneCode,
          hint: phoneMask,
          placeholder: Strings.of(context).phoneInputPlacaholder,
          keyboardType: TextInputType.phone,
          onChanged: (val) => profileManager.onPhoneChanged(val ?? ''),
          maxLength: phoneMask.length,
        ),
        YXListItem(
          borderType: YXListBorderType.bottomGap,
          lead: const YXIcon(YXIconData.card),
          title: Strings.of(context).linkCard,
          trail: const YXIcon(YXIconData.chevronsmall),
          onTap: () => navigator.openCardPage(),
        ),
        YXListItemSwitch(
          Strings.of(context).nightMode,
          value: isDarkTheme,
          borderType: YXListBorderType.bottomGap,
          onChanged: (val) {
            if (val) {
              themeManager.setDarkTheme();
            } else {
              themeManager.setLightTheme();
            }
          },
        ),
        YXListItem(
          borderType: YXListBorderType.bottomGap,
          title: Strings.of(context).deleteProfile,
          onTap: profileManager.onDeleteProfileTapped,
        ),
      ],
    );
  }
}

class ProfileInput extends HookWidget {
  final String? mask;
  final String? initialText;
  final String? hint;
  final String? placeholder;
  final TextInputType? keyboardType;
  final ValueChanged<String?>? onChanged;
  final int? maxLength;
  const ProfileInput({
    Key? key,
    this.mask,
    this.initialText,
    this.hint,
    this.placeholder,
    this.keyboardType,
    this.onChanged,
    this.maxLength,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final controller = mask == null
        ? useTextEditingController(text: initialText)
        : useMaskTextController(
            mask: mask ?? '',
            text: initialText,
          );

    return YXListInput(
      placeholderHasDots: false,
      borderType: YXListBorderType.bottom,
      hint: hint,
      controller: controller,
      keyboardType: keyboardType,
      placeholder: placeholder,
      onChanged: onChanged,
      maxLength: maxLength ?? TextField.noMaxLength,
    );
  }
}
