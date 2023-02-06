import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:models/models.dart';
import '../build/providers.dart';
import '../common/broken/broken_widget.dart';

import 'ui/answer/broken/state_holder.dart';

final answerPageBrokenStateHolderProvider =
    StateNotifierProvider.autoDispose<AnswerPageBrokenStateHolder, BrokenType>(
  (ref) {
    final isBroken =
        ref.watch(isBrokenProvider(BugIds.supportAnswerOnInitCrush));

    return AnswerPageBrokenStateHolder(
      isBroken ? BrokenType.crushed : null,
    );
  },
);
