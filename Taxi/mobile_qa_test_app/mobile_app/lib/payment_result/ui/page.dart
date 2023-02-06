import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:flutter_txm_ui_components/components.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

import '../../utils/localization.dart';
import '../../utils/navigation/navigation_manager.dart';

class PaymentResultPage extends ConsumerWidget {
  const PaymentResultPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) => TXMScaffold(
        appBar: TXMScaffoldAppBar(
          actions: [
            IconButton(
              onPressed:
                  ref.watch(navigationManagerProvider).popAllAndOpenShopPage,
              icon: const YXIcon(
                YXIconData.cross,
              ),
            ),
          ],
        ),
        header: TXMScaffoldHeaderSliver(
          Strings.of(context).paymentResultTitle,
        ),
        actions: TXMScaffoldActions(
          isOverflow: true,
          isRounded: true,
          primary: YXButton(
            onTap: ref.watch(navigationManagerProvider).popAllAndOpenShopPage,
            title: Strings.of(context).paymentResultButtonTitle,
          ),
        ),
        body: Center(
          child: SvgPicture.asset(
            'assets/ok.svg',
          ),
        ),
      );
}
