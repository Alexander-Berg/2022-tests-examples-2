import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../../build/providers.dart';
import 'broken_strings.dart';

final maybeBrokenStringsProvider = Provider(
  (ref) => MaybeBrokenStrings(
    ref.watch(buildStateHolderProvider),
  ),
);
