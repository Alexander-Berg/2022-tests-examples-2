import 'package:flutter/material.dart';
import 'package:flutter_txm_ui_components/components.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:models/models.dart';

import '../../build/providers.dart';
import '../routes.dart';
import 'broken/broken_navigation_manager.dart';
import 'navigation_state_holder.dart';

final navigationManagerProvider = Provider<NavigationManager>(
  (ref) {
    final isBroken =
        ref.watch(isBrokenProvider(BugIds.navigateFromCategoryToShop));

    if (isBroken) {
      return BrokenNavigationManager(
        ref.watch(navigationKeyProvider),
      );
    }

    return NavigationManager(
      ref.watch(navigationKeyProvider),
    );
  },
);

class NavigationManager {
  final GlobalKey<NavigatorState> _navigatorKey;

  NavigationManager(GlobalKey<NavigatorState> navigatorKey)
      : _navigatorKey = navigatorKey;

  void openAuthPage() {
    _navigatorKey.currentState?.pushNamed(AppRoutes.auth);
  }

  void openBuildPage() {
    _navigatorKey.currentState?.pushReplacementNamed(AppRoutes.build);
  }

  void popAllAndOpenBuildPage() {
    _navigatorKey.currentState?.pushNamedAndRemoveUntil(
      AppRoutes.build,
      ModalRoute.withName('/'),
    );
  }

  void openSignUpPage() {
    _navigatorKey.currentState?.pushNamed(AppRoutes.signUp);
  }

  void openCodePage() {
    _navigatorKey.currentState?.pushNamed(AppRoutes.code);
  }

  void openPhonePage() {
    _navigatorKey.currentState?.pushNamed(AppRoutes.phone);
  }

  void openSupportQuestionsPage() {
    _navigatorKey.currentState?.pushNamed(AppRoutes.supportQuestions);
  }

  void openSupportAnswerPage() {
    _navigatorKey.currentState?.pushNamed(AppRoutes.supportAnswer);
  }

  void openProductPage(Product product) {
    _navigatorKey.currentState
        ?.pushNamed(AppRoutes.product, arguments: product);
  }

  void popAllAndOpenShopPage() {
    _navigatorKey.currentState?.pushNamedAndRemoveUntil(
      AppRoutes.shop,
      ModalRoute.withName('/'),
    );
  }

  void openCartPage() {
    _navigatorKey.currentState?.pushNamed(AppRoutes.cart);
  }

  void openCardPage() {
    _navigatorKey.currentState?.pushNamed(AppRoutes.card);
  }

  void openPaymentPage() {
    _navigatorKey.currentState?.pushNamed(AppRoutes.payment);
  }

  void openPaymentResultPage() {
    _navigatorKey.currentState?.pushNamed(AppRoutes.paymentResult);
  }

  void openAdressPage() {
    _navigatorKey.currentState?.pushNamed(AppRoutes.address);
  }

  void openProfilePage() {
    _navigatorKey.currentState?.pushNamed(AppRoutes.profile);
  }

  void openCategory(Category category) {
    _navigatorKey.currentState?.pushNamed(
      AppRoutes.category,
      arguments: category,
    );
  }

  void pop() {
    _navigatorKey.currentState?.pop();
  }
}
