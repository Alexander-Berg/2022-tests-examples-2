//ignore_for_file: argument_type_not_assignable
//ignore_for_file: undefined_identifier
//ignore_for_file: non_bool_condition
import 'package:flutter_txm_ui_components/components.dart';
import 'package:models/models.dart';

import '../../../utils/localization.dart';
import '../../build/domain/state_holder.dart';
import '../../build/providers.dart';

/// Для более элегантного решения потребуется кодоген
class MaybeBrokenStrings {
  final Build state;

  MaybeBrokenStrings(this.state);

  String phoneTitle(BuildContext context) {
    if (state.isBroken(BugIds.phoneTitleMisspell)) {
      return _break(Strings.of(context).phoneTitle);
    }

    return Strings.of(context).phoneTitle;
  }

  String _break(String text) => text.substring(0, text.length - 1);
}
