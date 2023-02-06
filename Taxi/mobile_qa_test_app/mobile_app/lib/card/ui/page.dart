import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:flutter_txm_ui_components/components.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

import '../../utils/localization.dart';
import '../providers.dart';
import 'domain/page_manager.dart';
import 'domain/state.dart';

class CardPage extends HookConsumerWidget {
  const CardPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    useEffect(
      () {
        ref.read(cardPageManagerProvider).onInit();
      },
      const [],
    );

    final formIsValid = ref.watch(
      cardPageStateHolderProvider.select((state) => state.formIsValid),
    );

    final isLoading = ref.watch(
      cardPageStateHolderProvider.select((state) => state.isLoading),
    );

    final pageManager = ref.watch(cardPageManagerProvider);

    return TXMScaffold(
      appBar: const TXMScaffoldAppBar(
        leadingIcon: YXIconData.back,
      ),
      header: TXMScaffoldHeaderSliver(
        Strings.of(context).cardTitle,
      ),
      actions: TXMScaffoldActions(
        primary: YXButton(
          state: formIsValid
              ? isLoading
                  ? ButtonState.loading
                  : ButtonState.enabled
              : ButtonState.disabled,
          title: Strings.of(context).cardButtonTitle,
          onTap: pageManager.saveCard,
        ),
      ),
      body: isLoading
          ? Center(
              child: YXLoadingText(text: Strings.of(context).loading),
            )
          : Column(
              children: [
                YXListText(
                  text: Strings.of(context).cardBody,
                  borderType: YXListBorderType.none,
                ),
                const _CardForm(),
              ],
            ),
    );
  }
}

class _CardForm extends HookConsumerWidget {
  const _CardForm({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final validityPeriodFocus = useFocusNode();
    final cvvFocus = useFocusNode();
    final ownerFocus = useFocusNode();

    final pageManager = ref.watch(cardPageManagerProvider);

    return Column(
      children: [
        _CardNumberInput(
          pageManager: pageManager,
          onEditingComplete: validityPeriodFocus.requestFocus,
        ),
        Row(
          children: [
            Expanded(
              child: _ValidityPeriodInput(
                pageManager: pageManager,
                onEditingComplete: cvvFocus.requestFocus,
              ),
            ),
            Expanded(
              child: _CvvInput(
                pageManager: pageManager,
                onEditingComplete: ownerFocus.requestFocus,
              ),
            ),
          ],
        ),
        _OwnerInput(
          pageManager: pageManager,
          onEditingComplete: pageManager.saveCard,
        ),
      ],
    );
  }
}

class _OwnerInput extends HookConsumerWidget {
  const _OwnerInput({
    Key? key,
    required this.pageManager,
    required this.onEditingComplete,
  }) : super(key: key);

  final CardPageManager pageManager;
  final VoidCallback onEditingComplete;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isValid = ref.watch(
      cardPageStateHolderProvider.select((state) => state.ownerInvalid),
    );

    final textController = useTextEditingController(
      text: ref.watch(
        cardPageStateHolderProvider.select(
          (state) => state.owner,
        ),
      ),
    );

    return _CardInput(
      isInvalid: isValid,
      onEditingComplete: onEditingComplete,
      onChanged: pageManager.onOwnerEditing,
      textController: textController,
      placeholder: Strings.of(context).ownerInputPlaceholder,
    );
  }
}

class _CvvInput extends HookConsumerWidget {
  const _CvvInput({
    Key? key,
    required this.pageManager,
    required this.onEditingComplete,
  }) : super(key: key);

  final CardPageManager pageManager;
  final VoidCallback onEditingComplete;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isValid = ref.watch(
      cardPageStateHolderProvider.select((state) => state.cvvInvalid),
    );

    final textController = useTextEditingController(
      text: ref.watch(
        cardPageStateHolderProvider.select(
          (state) => state.cvv,
        ),
      ),
    );

    final maxLength = ref.watch(cvvInputMaxLengthProvider);

    return _CardInput(
      isInvalid: isValid,
      onEditingComplete: onEditingComplete,
      onChanged: pageManager.onCvvEditing,
      textController: textController,
      maxLength: maxLength,
      keyboardType: TextInputType.number,
      placeholder: Strings.of(context).cvvInputPlaceholder,
      inputFormatters: [
        FilteringTextInputFormatter.digitsOnly,
        FilteringTextInputFormatter.digitsOnly,
      ],
    );
  }
}

class _ValidityPeriodInput extends HookConsumerWidget {
  const _ValidityPeriodInput({
    Key? key,
    required this.pageManager,
    required this.onEditingComplete,
  }) : super(key: key);

  final CardPageManager pageManager;
  final VoidCallback onEditingComplete;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isValid = ref.watch(
      cardPageStateHolderProvider
          .select((state) => state.validityPeriodInvalid),
    );

    final textController = useTextEditingController(
      text: ref.watch(
        cardPageStateHolderProvider.select(
          (state) => state.validityPeriod,
        ),
      ),
    );

    return _CardInput(
      isInvalid: isValid,
      onEditingComplete: onEditingComplete,
      onChanged: pageManager.onValidityPeriodEditing,
      textController: textController,
      maxLength: 4,
      keyboardType: TextInputType.number,
      placeholder: Strings.of(context).validityPeriodInputPlaceholder,
      inputFormatters: [
        FilteringTextInputFormatter.digitsOnly,
      ],
    );
  }
}

class _CardNumberInput extends HookConsumerWidget {
  const _CardNumberInput({
    Key? key,
    required this.pageManager,
    required this.onEditingComplete,
  }) : super(key: key);

  final CardPageManager pageManager;
  final VoidCallback onEditingComplete;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isValid = ref.watch(
      cardPageStateHolderProvider.select((state) => state.cardNumberInvalid),
    );

    final textController = useTextEditingController(
      text: ref.watch(
        cardPageStateHolderProvider.select(
          (state) => state.cardNumber,
        ),
      ),
    );

    return _CardInput(
      isInvalid: isValid,
      onEditingComplete: onEditingComplete,
      onChanged: pageManager.onCardNumberEditing,
      textController: textController,
      maxLength: 16,
      keyboardType: TextInputType.number,
      placeholder: Strings.of(context).cardInputPlaceholder,
      inputFormatters: [
        FilteringTextInputFormatter.digitsOnly,
      ],
    );
  }
}

class _CardInput extends StatelessWidget {
  final FocusNode? focusNode;
  final TextEditingController textController;
  final bool isInvalid;
  final String placeholder;
  final int? maxLength;
  final VoidCallback onEditingComplete;
  final Function(String) onChanged;
  final TextInputType? keyboardType;

  final List<TextInputFormatter>? inputFormatters;

  const _CardInput({
    Key? key,
    this.focusNode,
    this.inputFormatters,
    this.maxLength,
    required this.onChanged,
    required this.textController,
    required this.isInvalid,
    required this.placeholder,
    required this.onEditingComplete,
    this.keyboardType,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) => YXListInput(
        onEditingComplete: onEditingComplete,
        focusNode: focusNode,
        keyboardType: keyboardType,
        onChanged: onChanged,
        maxLength: maxLength ?? TextField.noMaxLength,
        borderType: YXListBorderType.bottom,
        placeholderHasDots: false,
        controller: textController,
        error: isInvalid ? placeholder : null,
        placeholder: placeholder,
        inputFormatters: inputFormatters,
      );
}
