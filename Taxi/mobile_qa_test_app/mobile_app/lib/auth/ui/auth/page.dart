import 'package:flutter_svg/flutter_svg.dart';
import 'package:flutter_txm_ui_components/components.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

import '../../../utils/localization.dart';
import '../../providers.dart';

class AuthPage extends ConsumerWidget {
  const AuthPage({Key? key}) : super(key: key);
  @override
  Widget build(BuildContext context, WidgetRef ref) => TXMScaffold(
        appBar: TXMScaffoldAppBar(
          title: Text(Strings.of(context).app_name),
        ),
        actions: TXMScaffoldActions(
          primary: YXButton(
            title: Strings.of(context).sign_in,
            onTap: () => ref.read(authManagerProvider).onSignInClicked(),
          ),
          secondary: YXButton(
            title: Strings.of(context).sign_up,
            onTap: () => ref.read(authManagerProvider).onSignUpClicked(),
          ),
          upperItems: [
            YXListItem(
              borderType: YXListBorderType.none,
              titleWidget: TXMMarkdownParser.parseMarkdown(
                text: Strings.of(context).enter_agreement,
              ),
            ),
          ],
        ),
        body: Center(
          child: SvgPicture.asset('assets/market_logo.svg'),
        ),
      );
}
