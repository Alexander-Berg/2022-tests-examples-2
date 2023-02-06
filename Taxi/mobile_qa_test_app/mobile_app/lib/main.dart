import 'package:flutter/material.dart';
import 'package:flutter_txm_ui_components/components.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

import 'common/env/env.dart';
import 'common/env/env_state_holder.dart';
import 'configs/app_state.dart';
import 'configs/configs_providers.dart';
import 'utils/localization.dart';
import 'utils/navigation/navigation_state_holder.dart';
import 'utils/routes.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) => ProviderScope(
        overrides: [
          envStateHolder.overrideWithValue(EnvStateHolder(Env.dev)),
        ],
        child: MyAppBody(),
      );
}

class MyAppBody extends ConsumerWidget {
  const MyAppBody({
    Key? key,
  }) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isLightTheme = ref.watch(appStateProvider.select((s) => s.isLight));

    return TXMToasterProvider(
      child: YXTheme(
        data: isLightTheme ? YXThemeData.light : YXThemeData.dark,
        child: TXMTheme(
          data: isLightTheme ? txmThemeLight : txmThemeDark,
          child: MaterialApp(
            navigatorKey: ref.watch(navigationKeyProvider),
            localizationsDelegates: localizationsDelegates,
            supportedLocales: supportedLocals,
            onGenerateRoute: onGenerateRoutes,
          ),
        ),
      ),
    );
  }
}
