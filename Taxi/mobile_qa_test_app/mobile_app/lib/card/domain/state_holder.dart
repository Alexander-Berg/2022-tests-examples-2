import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../models/card.dart';

class CardStateHolder extends StateNotifier<Card?> {
  CardStateHolder([Card? initial]) : super(initial);

  Card? getCard() => state;

  bool isCardSaved() => getCard() != null;

  void setCard(Card? card) => state = card;
}
