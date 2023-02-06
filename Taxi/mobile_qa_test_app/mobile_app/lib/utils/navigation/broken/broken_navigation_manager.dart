import 'package:flutter/src/widgets/framework.dart';
import 'package:flutter/src/widgets/navigator.dart';
import 'package:models/models.dart';

import '../../routes.dart';
import '../navigation_manager.dart';

class BrokenNavigationManager extends NavigationManager {
  final GlobalKey<NavigatorState> _navigatorKey;
  BrokenNavigationManager(GlobalKey<NavigatorState> navigatorKey)
      : _navigatorKey = navigatorKey,
        super(navigatorKey);

  @override
  void openCategory(Category category) {
    _navigatorKey.currentState?.pushNamed(AppRoutes.shop);
  }
}
