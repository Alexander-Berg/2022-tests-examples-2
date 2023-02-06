//ignore_for_file: argument_type_not_assignable
//ignore_for_file: undefined_getter

import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:models/models.dart';

import '../../../common/validation/models/validation_rules.dart';
import '../providers.dart';

final validationRulesProvider = Provider(
  (ref) => ValidationRules(
    isOwnerValid: ref.watch(isBrokenProvider(BugIds.validationIsOwnerValid))
        ? BrokenValidationRules.brokenIsOwnerValid
        : null,
  ),
);

class BrokenValidationRules {
  static bool brokenIsOwnerValid(String owner) => true;
}
