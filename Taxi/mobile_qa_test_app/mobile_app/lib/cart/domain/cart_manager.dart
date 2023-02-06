import 'package:models/models.dart';

import '../../auth/models/user.dart';
import '../../utils/navigation/navigation_manager.dart';
import '../../utils/toaster_manager.dart';
import '../api/cart_storage.dart';
import 'cart_state.dart';
import 'cart_state_holder.dart';

class CartManager {
  final CartDao cartDao;
  final CartStateHolder cartStateHolder;
  final User? currentUser;
  final NavigationManager navigationManager;
  final ToasterManager toasterManager;
  CartManager({
    required this.cartDao,
    required this.cartStateHolder,
    required this.currentUser,
    required this.navigationManager,
    required this.toasterManager,
  });

  Future<void> onInit() async {
    final _currentUser = currentUser;
    if (_currentUser == null) {
      navigationManager.popAllAndOpenBuildPage();

      return;
    }
    final loadedState = await cartDao.cartState(_currentUser);
    cartStateHolder.setCart(loadedState ?? CartState([], _currentUser.phone));
  }

  Future<void> addProduct(Product product) async {
    try {
      cartStateHolder.addProduct(product);
      await cartDao.saveCartState(cartStateHolder.state);
    } on Exception catch (err) {
      toasterManager.showErrorMessage(err.toString());
    }
  }

  void removeProduct(Product product) {
    try {
      cartStateHolder.removeProduct(product);
      cartDao.saveCartState(cartStateHolder.state);
    } on Exception catch (err) {
      toasterManager.showErrorMessage(err.toString());
    }
  }

  void clear() {
    try {
      cartStateHolder.clear();
      cartDao.saveCartState(cartStateHolder.state);
    } on Exception catch (err) {
      toasterManager.showErrorMessage(err.toString());
    }
  }

  void onNextButtonTapped() => navigationManager.openPaymentPage();
}
