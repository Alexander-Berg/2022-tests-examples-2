import 'package:flutter_txm_ui_components/components.dart';
import '../../../../../utils/localization.dart';

import 'fio_form.dart';

class SignUpBody extends StatelessWidget {
  final ValueChanged<String>? onSurnameChanged;
  final ValueChanged<String>? onNameChanged;
  final ValueChanged<String>? onPatronymicChanged;
  const SignUpBody({
    Key? key,
    this.onSurnameChanged,
    this.onNameChanged,
    this.onPatronymicChanged,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) => Column(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          YXListText(
            text: Strings.of(context).buildBody,
            borderType: YXListBorderType.none,
          ),
          FioForm(
            onSurnameChanged: onSurnameChanged,
            onNameChanged: onNameChanged,
            onPatronymicChanged: onPatronymicChanged,
          ),
        ],
      );
}
