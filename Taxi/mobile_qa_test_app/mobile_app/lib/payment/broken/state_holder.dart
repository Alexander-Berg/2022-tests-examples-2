import 'package:state_notifier/state_notifier.dart';

import '../../common/broken/broken_widget.dart';

class PaymentPageBrokenStateHolder extends StateNotifier<BrokenType> {
  PaymentPageBrokenStateHolder([BrokenType? state])
      : super(state ?? BrokenType.none);

  void freeze() => state = BrokenType.freezed;
}
