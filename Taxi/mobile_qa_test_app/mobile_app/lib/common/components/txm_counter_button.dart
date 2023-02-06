import 'package:flutter/material.dart';
import 'package:flutter_txm_ui_components/components.dart';
import 'txm_small_button.dart';

class TXMCounterButton extends StatelessWidget {
  const TXMCounterButton(
    this.initialValue, {
    required this.onDecrement,
    required this.onIncrement,
    Key? key,
  }) : super(key: key);

  final VoidCallback? onDecrement;
  final int initialValue;
  final VoidCallback? onIncrement;

  @override
  Widget build(BuildContext context) {
    final theme = YXTheme.of<YXThemeData>(context);

    return TXMSmallButton(
      main: Padding(
        padding: EdgeInsets.symmetric(horizontal: theme.module),
        child: Row(
          children: [
            GestureDetector(
              onTap: onDecrement,
              child: const YXIcon(YXIconData.minus, size: 12),
            ),
            SizedBox(width: theme.mu(3.75)),
            Text('$initialValue'),
            SizedBox(width: theme.mu(3.75)),
            GestureDetector(
              onTap: onIncrement,
              child: const YXIcon(YXIconData.plus, size: 12),
            ),
          ],
        ),
      ),
      textStyle: theme.textTheme.caption2Bold,
    );
  }
}
