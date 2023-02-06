import 'package:flutter/material.dart';
import 'package:flutter_txm_ui_components/components.dart';

class TXMSmallButton extends StatelessWidget {
  final Widget? lead;
  final Widget? main;
  final Widget? trail;
  final String? title;
  final String? subtitle;
  final VoidCallback? onTap;
  final bool isRounded;
  final bool isLifted;
  final bool isAccent;
  final bool isPressed;
  final ButtonState state;
  final TextStyle? textStyle;

  const TXMSmallButton({
    this.lead,
    this.main,
    this.trail,
    this.title,
    this.subtitle,
    this.onTap,
    this.isRounded = false,
    this.isLifted = false,
    this.isAccent = false,
    this.isPressed = false,
    this.state = ButtonState.enabled,
    this.textStyle,
    Key? key,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final theme = YXTheme.of<YXThemeData>(context);

    return YXTheme(
      data: YXTheme.of<YXThemeData>(context).buttonTheme.copyWith(
            titleStyle: theme.textTheme.caption2.merge(textStyle),
            muBorderRadius: 1.25,
          ),
      child: SizedBox(
        height: theme.mu(4),
        child: YXButton(
          isRounded: isRounded,
          isLifted: isLifted,
          isAccent: isAccent,
          state: state,
          isPressed: isPressed,
          onTap: onTap,
          lead: lead,
          main: main,
          trail: trail,
          title: title,
          subtitle: subtitle,
        ),
      ),
    );
  }
}
