import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:models/models.dart';

class BuildStateHolder extends StateNotifier<Build> {
  BuildStateHolder([Build? state]) : super(state ?? Build.noBugs);

  void setBuild(Build? build) => state = build ?? Build.noBugs;
}

extension BrokenX on Build {
  bool isBroken(String bugKey) => bugs
      .where(
        (bug) => bug.id == bugKey,
      )
      .isNotEmpty;
}
