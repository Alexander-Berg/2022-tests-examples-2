import 'package:flutter/material.dart';
import 'package:flutter_txm_ui_components/components.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

import '../../utils/localization.dart';
import '../domain/app_loader_state_holder.dart';
import '../models/app_loader.dart';
import '../providers.dart';
import 'failed_loading_page.dart';
import 'loading_page.dart';

class AppLoaderPage extends ConsumerStatefulWidget {
  const AppLoaderPage({Key? key}) : super(key: key);

  @override
  _AppLoaderPageState createState() => _AppLoaderPageState();
}

class _AppLoaderPageState extends ConsumerState<AppLoaderPage> {
  @override
  void initState() {
    super.initState();

    ref.read(appLoaderManagerProvider).onInit();
  }

  @override
  Widget build(BuildContext context) => Consumer(
        builder: (context, ref, child) {
          final appLoaderState = ref.watch(appLoaderStateHolderProvider);
          if (appLoaderState is AppLoaderInProgress) {
            return const AppLoadingPage();
          } else if (appLoaderState is AppLoaderFailured) {
            return AppFailedLoadingPage(
              errorText: appLoaderState.message,
              retryText: Strings.of(context).retry_text,
              onRetryTap: () =>
                  ref.read(appLoaderManagerProvider).onRetrySetUp(),
            );
          }
          //Redirecting in the moment of reaching this line

          return TXMScaffold(body: const SizedBox.shrink());
        },
      );
}
