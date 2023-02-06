import '../../../common/broken/broken_widget.dart';

class UserPageBrokenState {
  final BrokenType brokenType;
  final bool shouldBeOnInitCrushed;
  final bool shouldBeOnAddTapCrushed;

  UserPageBrokenState({
    this.brokenType = BrokenType.none,
    this.shouldBeOnAddTapCrushed = false,
    this.shouldBeOnInitCrushed = false,
  });
}
