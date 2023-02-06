//ignore_for_file: argument_type_not_assignable
//ignore_for_file: undefined_identifier
//ignore_for_file: non_bool_condition
import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../providers.dart';

class User {
  int? age;
  String? name;

  User({this.age, this.name});
}

final userStateHolderProvider =
    StateNotifierProvider<UserStateHolder, User>((ref) {
  if (ref.watch(isBrokenProvider(BugKeys.userChangeData))) {
    return BrokenUserStateHolder();
  }

  return UserStateHolder();
});

class BrokenUserStateHolder extends UserStateHolder {
  @override
  void changeName(String name) {
    state = User(name: 'awesome $name');
  }
}

class UserStateHolder extends StateNotifier<User> {
  UserStateHolder([User? state]) : super(state ?? User());

  void changeAge(int age) {
    state = User(age: age);
  }

  void changeName(String name) {
    state = User(name: name);
  }
}
