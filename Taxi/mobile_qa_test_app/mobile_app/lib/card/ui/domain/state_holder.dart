import 'package:state_notifier/state_notifier.dart';

import '../../../common/converters/date_time_converter.dart';
import '../../../common/validation/models/validation_rules.dart';
import '../../models/card.dart';
import 'state.dart';

class CardPageStateHolder extends StateNotifier<CardPageState> {
  ValidationRules _validationRules;

  CardPageStateHolder(
    this._validationRules, [
    CardPageState? cardPageState,
  ]) : super(cardPageState ?? const CardPageState());

  @override
  CardPageState get state => super.state;

  void _updateState(CardPageState state) {
    this.state = state;
  }

  void setIsLoading(bool value) => state = state.copyWith(isLoading: value);

  void setInitialCardData(Card? card) => state = state.copyWith(
        cardNumber: card?.cardNumber ?? '',
        cvv: card?.cvv ?? '',
        validityPeriod: card?.validityPeriod.toCardPageFormattedString() ?? '',
        owner: card?.owner ?? '',
      );

  void editOwner(String owner) => _updateState(
        state.copyWith(
          owner: owner,
          ownerInvalid: !_validationRules.isOwnerValid(owner),
        ),
      );
  void editCvv(String cvv) => _updateState(
        state.copyWith(
          cvv: cvv,
          cvvInvalid: !_validationRules.isCvvValid(cvv),
        ),
      );

  void editCardNumber(String cardNumber) => _updateState(
        state.copyWith(
          cardNumber: cardNumber,
          cardNumberInvalid: !_validationRules.isCardNumberValid(cardNumber),
        ),
      );
  void editValidityPeriod(String validityPeriod) {
    _updateState(
      state.copyWith(
        validityPeriod: validityPeriod,
        validityPeriodInvalid:
            !_validationRules.isValidityPeriodValid(validityPeriod),
      ),
    );
  }

  bool formIsValid() => state.formIsValid;
}
