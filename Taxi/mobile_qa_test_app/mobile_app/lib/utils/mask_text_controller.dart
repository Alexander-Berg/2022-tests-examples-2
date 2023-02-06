import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:flutter_txm_ui_components/components.dart';

/// Параметры:
///
///    [text]
///
///    [mask]
///
///    [translator]
const useMaskTextController = _MaskTextControllerCreator();

class _MaskTextControllerCreator {
  const _MaskTextControllerCreator();

  TXMStickyMaskedTextController call({
    required String mask,
    String? text,
    Map<String, RegExp>? translator,
  }) =>
      use(_MaskTextControllerHook(
        text: text,
        mask: mask,
        translator: translator ??
            {
              '0': RegExp(r'[0-9]'),
              '9': RegExp(r'[0-9]'),
            },
      ));
}

class _MaskTextControllerHook extends Hook<TXMStickyMaskedTextController> {
  final String? text;
  final String? mask;
  final Map<String, RegExp>? translator;

  const _MaskTextControllerHook({
    this.text,
    this.mask,
    this.translator,
  });

  @override
  HookState<TXMStickyMaskedTextController, _MaskTextControllerHook>
      createState() => _MaskTextControllerHookState();
}

class _MaskTextControllerHookState
    extends HookState<TXMStickyMaskedTextController, _MaskTextControllerHook> {
  late final TXMStickyMaskedTextController _maskedTextController =
      TXMStickyMaskedTextController(
    text: hook.text,
    mask: hook.mask,
    translator: hook.translator,
  );

  @override
  void dispose() => _maskedTextController.dispose();

  @override
  TXMStickyMaskedTextController build(BuildContext context) =>
      _maskedTextController;

  @override
  String? get debugLabel => 'useMaskTextController';
}
