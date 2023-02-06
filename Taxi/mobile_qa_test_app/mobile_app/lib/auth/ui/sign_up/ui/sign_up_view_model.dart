import '../../../../common/validation/models/validation_rules.dart';
import '../domain/signup_page_state.dart';

class SignUpViewModel {
  final SignUpPageState state;
  final ValidationRules validator;
  final bool isValid;

  SignUpViewModel({
    required this.state,
    required this.validator,
  }) : isValid = validator.isNameValid(state.name) &&
            validator.isNameValid(state.surname);

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) {
      return true;
    }

    return other is SignUpViewModel &&
        other.state == state &&
        other.validator == validator &&
        other.isValid == isValid;
  }

  @override
  int get hashCode => state.hashCode ^ validator.hashCode ^ isValid.hashCode;
}
