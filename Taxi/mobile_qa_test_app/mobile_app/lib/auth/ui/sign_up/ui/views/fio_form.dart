// import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:flutter_txm_ui_components/components.dart';
import '../../../../../utils/localization.dart';

class FioForm extends StatelessWidget {
  final ValueChanged<String>? onSurnameChanged;
  final ValueChanged<String>? onNameChanged;
  final ValueChanged<String>? onPatronymicChanged;
  const FioForm({
    Key? key,
    this.onSurnameChanged,
    this.onNameChanged,
    this.onPatronymicChanged,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) => Column(
        children: [
          YXListInput(
            hint: Strings.of(context).surnameInputHint,
            placeholderHasDots: false,
            useHintAsPlaceholder: true,
            borderType: YXListBorderType.bottom,
            onChanged: onSurnameChanged,
          ),
          YXListInput(
            borderType: YXListBorderType.bottom,
            hint: Strings.of(context).nameInputHint,
            placeholderHasDots: false,
            useHintAsPlaceholder: true,
            onChanged: onNameChanged,
          ),
          YXListInput(
            hint: Strings.of(context).patronymicInputHint,
            placeholderHasDots: false,
            useHintAsPlaceholder: true,
            borderType: YXListBorderType.bottom,
            onChanged: onPatronymicChanged,
          ),
        ],
      );
}
