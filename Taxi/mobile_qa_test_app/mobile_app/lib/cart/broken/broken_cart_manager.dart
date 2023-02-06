import 'package:models/models.dart';

import '../../auth/models/user.dart';
import '../../utils/navigation/navigation_manager.dart';
import '../../utils/toaster_manager.dart';

import '../api/cart_storage.dart';
import '../domain/cart_manager.dart';
import '../domain/cart_state_holder.dart';

class BrokenCartManager extends CartManager {
  final bool isIncrementBroken;
  final bool isDecrementBroken;
  final bool isClearBroken;

  BrokenCartManager(
    CartDao cartDao,
    CartStateHolder cartStateHolder,
    User? currentUser,
    NavigationManager navigationManager,
    ToasterManager toasterManager, {
    required this.isIncrementBroken,
    required this.isDecrementBroken,
    required this.isClearBroken,
  }) : super(
          cartDao: cartDao,
          cartStateHolder: cartStateHolder,
          currentUser: currentUser,
          navigationManager: navigationManager,
          toasterManager: toasterManager,
        );

  @override
  void clear() {
    if (isClearBroken) {
      //Nothing
    } else {
      super.clear();
    }
  }

  @override
  void removeProduct(Product product) {
    if (isDecrementBroken) {
      super.addProduct(product);
    } else {
      super.removeProduct(product);
    }
  }

  @override
  Future<void> addProduct(Product product) async {
    if (isIncrementBroken) {
      await Future.wait([
        super.addProduct(product),
        super.addProduct(product),
      ]);
    } else {
      await super.addProduct(product);
    }
  }
}
