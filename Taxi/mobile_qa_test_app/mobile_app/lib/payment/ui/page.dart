import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:flutter_txm_ui_components/components.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../../common/broken/broken_widget.dart';

import '../../utils/localization.dart';
import '../domain/state.dart';
import '../providers.dart';
import 'payment_options.dart';

class PaymentPage extends HookConsumerWidget {
  const PaymentPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    useEffect(
      () {
        ref.read(paymentPageManager).onInit();
      },
      const [],
    );

    final brokenState = ref.watch(paymentPageBrokenStateHolderProvider);

    final pageManager = ref.watch(paymentPageManager);

    final isSelectedSmth = ref.watch(
          paymentPageStateHolderProvider.select((state) => state.selected),
        ) !=
        PaymentOption.none;

    return BrokenWidget(
      brokenType: brokenState,
      child: TXMScaffold.slivers(
        appBar: const TXMScaffoldAppBar(
          leadingIcon: YXIconData.back,
        ),
        header: TXMScaffoldHeaderSliver(
          Strings.of(context).paymentTitle,
        ),
        actions: TXMScaffoldActions(
          isOverflow: true,
          isRounded: true,
          primary: YXButton(
            title: Strings.of(context).paymentButtonTitle,
            state: isSelectedSmth ? ButtonState.enabled : ButtonState.disabled,
            subtitle: '123 ${Strings.of(context).rubleSign}',
            onTap: pageManager.pay,
          ),
        ),
        slivers: const [
          PaymentOptions(),
        ],
      ),
    );
  }
}
