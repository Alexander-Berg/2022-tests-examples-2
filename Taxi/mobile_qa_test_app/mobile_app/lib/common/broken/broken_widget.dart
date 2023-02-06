import 'package:flutter/material.dart';
import 'package:flutter_txm_ui_components/components.dart';

class BrokenWidget extends StatelessWidget {
  final BrokenType brokenType;

  final Widget child;

  const BrokenWidget({
    this.brokenType = BrokenType.none,
    required this.child,
    Key? key,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    if (brokenType == BrokenType.freezed) {
      /// Эмулируем фриз
      return WillPopScope(
        onWillPop: () async => false,
        child: IgnorePointer(
          child: child,
        ),
      );
    } else if (brokenType == BrokenType.crushed) {
      return Container(
        /// В релизной сборке ошибка на экране отображается серым цветом
        color: Colors.grey,
      );
    }

    return child;
  }
}

enum BrokenType {
  crushed,
  freezed,
  none,
}
