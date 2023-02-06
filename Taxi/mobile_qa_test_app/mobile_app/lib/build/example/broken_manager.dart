//ignore_for_file: argument_type_not_assignable
//ignore_for_file: undefined_identifier
//ignore_for_file: non_bool_condition
import 'package:hooks_riverpod/hooks_riverpod.dart';

import '../providers.dart';
import 'broken_state_holder.dart';

/// Провайдер будет являться фабрикой, которая будет создавать
/// нужный инстанс мэнэджера
final userManagerProvider = Provider<UserManager>((ref) {
  final state = ref.watch(userStateHolderProvider.notifier);

  if (ref.watch(isBrokenProvider(BugKeys.userChangeData))) {
    return BrokenUserManager(
      state,
    );
  }

  return UserManager(state);
});

class BrokenUserManager extends UserManager {
  BrokenUserManager(
    UserStateHolder state,
  ) : super(state);

  @override
  void changeAge(int age) {
    state.changeAge(age + 1);
  }
}

class UserManager {
  UserStateHolder state;

  UserManager(
    this.state,
  );

  void changeAge(int age) {
    state.changeAge(age);
  }

  void changeName(String name) {
    state.changeName(name);
  }
}
