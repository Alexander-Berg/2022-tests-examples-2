import 'package:flutter/material.dart';
import 'package:flutter_txm_ui_components/components.dart';

class AppFailedLoadingPage extends StatelessWidget {
  final String errorText;
  final String retryText;
  final VoidCallback onRetryTap;
  const AppFailedLoadingPage({
    required this.retryText,
    required this.errorText,
    required this.onRetryTap,
    Key? key,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) => TXMScaffold(
        body: Center(
          child: TXMErrorView(
            errorText: errorText,
            onRetryTap: onRetryTap,
            retryText: retryText,
          ),
        ),
      );
}
