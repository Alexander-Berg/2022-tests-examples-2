import 'package:flutter/material.dart';
import 'package:flutter_txm_ui_components/components.dart';
import '../../utils/localization.dart';

class AppLoadingPage extends StatelessWidget {
  const AppLoadingPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) => TXMScaffold(
        body: Center(
          child: YXLoadingText(
            text: Strings.of(context).loading,
          ),
        ),
      );
}
