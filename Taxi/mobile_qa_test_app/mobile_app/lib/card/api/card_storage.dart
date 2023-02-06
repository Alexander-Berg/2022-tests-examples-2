import 'package:yx_persist/yx_persist.dart';

import '../../common/local_storage/local_storage.dart';
import '../models/card.dart';

class CardDao extends YxDao<String, Card> {
  @override
  String primaryKeyOf(Card card) => StorageKeys.cardData;

  Future<Card?> getCard() async => getByKey(StorageKeys.cardData);

  Future<void> saveCard(Card card) async => put(card);

  @override
  Card fromDb(Map<String, dynamic> json) => Card.fromJson(json);

  @override
  Map<String, dynamic> toDb(Card card) => card.toJson();
}
