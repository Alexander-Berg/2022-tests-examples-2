import 'package:freezed_annotation/freezed_annotation.dart';

part 'card.freezed.dart';
part 'card.g.dart';

@freezed
class Card with _$Card {
  const factory Card({
    @JsonKey(name: 'card_number') required final String cardNumber,
    @JsonKey(name: 'cvv') required final String cvv,
    @JsonKey(name: 'owner') required final String owner,
    @JsonKey(name: 'validity_period') required final DateTime validityPeriod,
  }) = _Card;
  factory Card.fromJson(Map<String, dynamic> json) => _$CardFromJson(json);
}
