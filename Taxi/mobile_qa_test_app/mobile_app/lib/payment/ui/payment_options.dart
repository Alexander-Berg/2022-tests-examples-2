import 'package:flutter_svg/flutter_svg.dart';
import 'package:flutter_txm_ui_components/components.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../../utils/assets.dart';

import '../../utils/localization.dart';
import '../domain/state.dart';
import '../providers.dart';

class PaymentOptions extends ConsumerWidget {
  const PaymentOptions({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final containsCard = ref.watch(
      paymentPageStateHolderProvider.select(
        (state) => state.enabledOptions.contains(PaymentOption.card),
      ),
    );

    final pageManager = ref.watch(paymentPageManager);

    final selectedOption = ref.watch(
      paymentPageStateHolderProvider.select((state) => state.selected),
    );

    return SliverList(
      delegate: SliverChildListDelegate(
        [
          YXListItemCheck(
            Strings.of(context).paymentCardOption,
            lead: SvgPicture.asset(Assets.svgCard),
            borderType: YXListBorderType.bottom,
            value: selectedOption == PaymentOption.card,
            isDisabled: !containsCard,
            onChanged: (flag) => flag
                ? pageManager.onChoosePaymentOption(PaymentOption.card)
                : null,
          ),
          YXListItemCheck(
            Strings.of(context).paymentCashOption,
            lead: SvgPicture.asset(Assets.svgCash),
            borderType: YXListBorderType.bottom,
            value: selectedOption == PaymentOption.cash,
            onChanged: (flag) => flag
                ? pageManager.onChoosePaymentOption(PaymentOption.cash)
                : null,
          ),
        ],
      ),
    );
  }
}
