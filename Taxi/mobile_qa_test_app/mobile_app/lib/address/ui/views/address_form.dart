import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:flutter_txm_ui_components/components.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

import '../../../auth/domain/user_state_holder.dart';
import '../../../utils/localization.dart';
import '../../address_providers.dart';
import 'house_form.dart';

class AddressForm extends HookConsumerWidget {
  const AddressForm({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final pageManager = ref.watch(addressPageManager);
    final address = ref.watch(userStateProvider.select((u) => u?.address));
    final cityInputController = useTextEditingController(text: address?.city);
    final streetInputController =
        useTextEditingController(text: address?.street);

    return Column(
      children: [
        YXListInput(
          controller: cityInputController,
          borderType: YXListBorderType.bottom,
          placeholderHasDots: false,
          placeholder: Strings.of(context).cityInputPlaceholder,
          onChanged: pageManager.onChangedCity,
        ),
        YXListInput(
          controller: streetInputController,
          borderType: YXListBorderType.bottom,
          placeholderHasDots: false,
          placeholder: Strings.of(context).streetInputPlaceholder,
          onChanged: pageManager.onChangedStreet,
        ),
        const HouseForm(),
      ],
    );
  }
}
