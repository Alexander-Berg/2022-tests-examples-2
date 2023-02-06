import '../../../common/converters/date_time_converter.dart';
import '../../../utils/navigation/navigation_manager.dart';
import '../../../utils/toaster_manager.dart';
import '../../domain/manager.dart';
import '../../domain/state_holder.dart';
import 'state_holder.dart';

class CardPageManager {
  final CardPageStateHolder state;
  final CardManager cardManager;
  final CardStateHolder cardState;
  final NavigationManager navigationManager;
  final ToasterManager toasterManager;

  CardPageManager({
    required this.state,
    required this.cardManager,
    required this.cardState,
    required this.navigationManager,
    required this.toasterManager,
  });

  Future<void> onInit() async {
    state.setIsLoading(true);
    await cardManager.init();
    final card = cardState.state;
    state.setInitialCardData(card);
    state.setIsLoading(false);
  }

  Future<void> saveCard() async {
    if (!state.formIsValid()) return;
    state.setIsLoading(true);
    try {
      await cardManager.saveCard(
        cardNumber: state.state.cardNumber,
        validityPeriod: state.state.validityPeriod.toCardFormattedDateTime(),
        cvv: state.state.cvv,
        owner: state.state.owner,
      );
      navigationManager.pop();
    } on Exception catch (e) {
      toasterManager.showErrorMessage(e.toString());
    } finally {
      state.setIsLoading(false);
    }
  }

  void onCardNumberEditing(String cardNumber) =>
      state.editCardNumber(cardNumber);

  void onValidityPeriodEditing(String validityPeriod) =>
      state.editValidityPeriod(validityPeriod);

  void onCvvEditing(String cvv) => state.editCvv(cvv);

  void onOwnerEditing(String owner) => state.editOwner(owner);
}
