import 'package:flutter_txm_ui_components/components.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

import '../../utils/formatters.dart';
import '../../utils/localization.dart';
import '../address_providers.dart';
import 'views/address_form.dart';

class AddressPage extends ConsumerWidget {
  const AddressPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isValid = ref.watch(
      addressPageViewModelProvider.select((v) => v.isAllDataValid),
    );
    final pageManager = ref.watch(addressPageManager);

    return TXMScaffold.list(
      appBar: const TXMScaffoldAppBar(
        leadingIcon: YXIconData.back,
      ),
      header: TXMScaffoldHeaderSliver(
        Strings.of(context).addressTitle,
      ),
      actions: TXMScaffoldActions(
        isRounded: true,
        isOverflow: true,
        primary: YXButton(
          onTap: pageManager.onNextButtonTapped,
          title: Strings.of(context).addressButtonTitle,
          state: isValid ? ButtonState.enabled : ButtonState.disabled,
          subtitle: 123.toPrice(
            currencySymbol: Strings.of(context).rubleSign,
            locale: Localizations.localeOf(context).toLanguageTag(),
            fractionDigits: 0,
          ),
        ),
      ),
      children: [
        const AddressForm(),
        YXListInput(
          borderType: YXListBorderType.bottom,
          placeholderHasDots: false,
          placeholder: Strings.of(context).commentInputPlaceholder,
        ),
      ],
    );
  }
}
