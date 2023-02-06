import 'package:hooks_riverpod/hooks_riverpod.dart';

import 'local_storage.dart';

final localStorageProvider = Provider((ref) => LocalStorage());

final usersDaoProvider = Provider((ref) {
  final storage = ref.watch(localStorageProvider);

  return storage.usersDataDao;
});
