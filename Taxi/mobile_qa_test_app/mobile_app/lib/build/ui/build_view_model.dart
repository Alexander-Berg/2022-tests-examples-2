// ignore_for_file: avoid_equals_and_hash_code_on_mutable_classes

import '../../../../common/validation/models/validation_rules.dart';
import 'domain/state.dart';

class CodeViewModel {
  final BuildPageState state;
  final ValidationRules validator;
  final bool isValid;

  CodeViewModel({
    required this.state,
    required this.validator,
  }) : isValid = validator.isBuildCodeValid(state.buildCode);

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) {
      return true;
    }

    return other is CodeViewModel &&
        other.state == state &&
        other.validator == validator &&
        other.isValid == isValid;
  }

  @override
  int get hashCode => state.hashCode ^ validator.hashCode ^ isValid.hashCode;
}
