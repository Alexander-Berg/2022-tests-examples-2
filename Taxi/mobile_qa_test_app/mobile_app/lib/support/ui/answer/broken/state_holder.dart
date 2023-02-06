import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:state_notifier/state_notifier.dart';

import '../../../../common/broken/broken_widget.dart';

class AnswerPageBrokenStateHolder extends StateNotifier<BrokenType> {
  AnswerPageBrokenStateHolder([BrokenType? state])
      : super(state ?? BrokenType.none);
}
