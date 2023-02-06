import 'package:hooks_riverpod/hooks_riverpod.dart';

import '../../common/validation/models/validation_rules.dart';
import '../../common/validation/providers.dart';
import '../domain/profile_page_state.dart';
import '../providers.dart';

final profileViewModel = Provider.autoDispose((ref) => ProfileViewModel(
      state: ref.watch(profilePageStateHolder),
      validator: ref.watch(validationRulesProvider),
    ));

class ProfileViewModel {
  final ProfilePageState state;
  final ValidationRules validator;
  final bool isValid;
  ProfileViewModel({
    required this.state,
    required this.validator,
  }) : isValid = validator.isNameValid(state.name) &&
            validator.isNameValid(state.surname) &&
            validator.isPhoneValid(state.phone);

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) {
      return true;
    }

    return other is ProfileViewModel &&
        other.state == state &&
        other.validator == validator &&
        other.isValid == isValid;
  }

  @override
  int get hashCode => state.hashCode ^ validator.hashCode ^ isValid.hashCode;
}
