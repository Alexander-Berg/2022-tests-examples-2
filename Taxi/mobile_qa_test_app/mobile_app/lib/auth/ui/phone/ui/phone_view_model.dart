import '../../../../common/validation/models/validation_rules.dart';
import '../domain/phone_page_state.dart';

class PhoneViewModel {
  final PhonePageState state;
  final ValidationRules validator;
  final bool isValid;

  PhoneViewModel({
    required this.state,
    required this.validator,
  }) : isValid = validator.isPhoneValid(state.phone);

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) {
      return true;
    }

    return other is PhoneViewModel &&
        other.state == state &&
        other.validator == validator &&
        other.isValid == isValid;
  }

  @override
  int get hashCode => state.hashCode ^ validator.hashCode ^ isValid.hashCode;
}
