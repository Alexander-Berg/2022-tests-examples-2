import '../../utils/toaster_manager.dart';
import '../api/card_storage.dart';
import '../models/card.dart';
import 'state_holder.dart';

class CardManager {
  CardStateHolder state;
  CardDao cardDao;
  ToasterManager toasterManager;

  CardManager({
    required this.state,
    required this.cardDao,
    required this.toasterManager,
  });

  Future<void> init() async {
    Card? card;
    try {
      card = null;
      card = await cardDao.getCard();
      state.setCard(card);
    } on Exception catch (e) {
      toasterManager.showErrorMessage(e.toString());
    }
  }

  Future<void> saveCard({
    required String cardNumber,
    required DateTime validityPeriod,
    required String cvv,
    required String owner,
  }) async {
    final card = Card(
      cardNumber: cardNumber,
      cvv: cvv,
      owner: owner,
      validityPeriod: validityPeriod,
    );
    await cardDao.saveCard(card);
    state.setCard(card);
  }
}
