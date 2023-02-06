// ignore_for_file: dead_code

import 'package:flutter/services.dart';
import 'package:flutter_txm_ui_components/components.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

import '../../utils/localization.dart';
import '../providers.dart';

class BuildPage extends ConsumerWidget {
  const BuildPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isLoading = ref.watch(
      buildPageStateHolderProvider.select((state) => state.isProgress),
    );

    return YXLoadingWidget(
      isLoading: isLoading,
      child: TXMScaffold(
        appBar: TXMScaffoldAppBar(
          centerTitle: false,
          title: Text(
            Strings.of(context).buildTitle,
          ),
        ),
        actions: const _BuildActions(),
        body: const _BuildBody(),
      ),
    );
  }
}

class _BuildActions extends ConsumerWidget {
  const _BuildActions({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final manager = ref.watch(buildManagerProvider);
    final isValid =
        ref.watch(buildViewModelProvider.select((vm) => vm.isValid));

    return TXMScaffoldActions(
      isRounded: true,
      primary: YXButton(
        title: Strings.of(context).start,
        onTap: manager.onEnter,
        state: isValid ? ButtonState.enabled : ButtonState.disabled,
      ),
    );
  }
}

class _BuildBody extends ConsumerWidget {
  const _BuildBody({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final manager = ref.watch(buildManagerProvider);

    return Column(
      children: [
        YXListText(
          text: Strings.of(context).buildBody,
        ),
        YXListInput(
          hint: Strings.of(context).buildInputHint,
          placeholderHasDots: false,
          useHintAsPlaceholder: true,
          onChanged: manager.onBuildCodeChanged,
          borderType: YXListBorderType.bottom,
          keyboardType: TextInputType.number,
          inputFormatters: [
            FilteringTextInputFormatter.digitsOnly,
          ],
        ),
      ],
    );
  }
}
