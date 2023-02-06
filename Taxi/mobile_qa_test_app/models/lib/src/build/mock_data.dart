import '../../models.dart';

final build1 = Build(
  id: '1',
  bugs: bugs1,
);
final build2 = Build(
  id: '2',
  bugs: bugs2,
);

final bugs1 = const [
  Bug(
    id: BugIds.shopProductOnIncrementDouble,
  ),
  Bug(
    id: BugIds.phoneTitleMisspell,
  ),
  Bug(
    id: BugIds.supportAnswerOnInitCrush,
  ),
  Bug(
    id: BugIds.navigateFromCategoryToShop,
  ),
];

final bugs2 = const [
  Bug(
    id: BugIds.profileOnSaveDoesNotWork,
  ),
  Bug(
    id: BugIds.paymentOptionsOnTapFreezed,
  ),
  Bug(
    id: BugIds.cardCvvInputLength4,
  ),
  Bug(
    id: BugIds.cartClearDoesNotWork,
  ),
  Bug(
    id: BugIds.shopProductOnDecrementInverse,
  ),
];
