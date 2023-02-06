import '../../../../common/validation/models/validation_rules.dart';
import '../domain/code_page_state.dart';

class CodeViewModel {
  final CodePageState state;
  final ValidationRules validator;
  final bool isValid;

  CodeViewModel({
    required this.state,
    required this.validator,
  }) : isValid = validator.isCodeValid(state.code);

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
