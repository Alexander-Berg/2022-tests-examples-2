import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:state_notifier/state_notifier.dart';

import 'env.dart';

final envStateHolder =
    StateNotifierProvider<EnvStateHolder, Env>((ref) => EnvStateHolder());

class EnvStateHolder extends StateNotifier<Env> {
  EnvStateHolder([Env state = Env.dev]) : super(state);

  @override
  Env get state => super.state;

  void changeEnv(Env newEnv) => state = newEnv;
}
