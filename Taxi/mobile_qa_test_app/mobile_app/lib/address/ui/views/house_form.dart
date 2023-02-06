import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:flutter_txm_ui_components/components.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../../../utils/localization.dart';
import '../../address_providers.dart';

class HouseForm extends HookConsumerWidget {
  const HouseForm({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final pageManager = ref.watch(addressPageManager);
    final pageStateHolder = ref.watch(addressPageStateHolderProvider.notifier);
    final address = pageStateHolder.address;
    final houseInputController = useTextEditingController(text: address.house);
    final corpusInputController =
        useTextEditingController(text: address.corpus);
    final buildingInputController =
        useTextEditingController(text: address.building);

    return Row(
      children: [
        Expanded(
          child: YXListInput(
            controller: houseInputController,
            borderType: YXListBorderType.bottom,
            placeholderHasDots: false,
            placeholder: Strings.of(context).houseInputPlaceholder,
            onChanged: pageManager.onChangedHouse,
          ),
        ),
        Expanded(
          child: YXListInput(
            controller: corpusInputController,
            borderType: YXListBorderType.bottom,
            placeholderHasDots: false,
            placeholder: Strings.of(context).corpusInputPlaceholder,
            onChanged: pageManager.onChangedCorpus,
          ),
        ),
        Expanded(
          child: YXListInput(
            controller: buildingInputController,
            borderType: YXListBorderType.bottom,
            placeholderHasDots: false,
            placeholder: Strings.of(context).buildingInputPlaceholder,
            onChanged: pageManager.onChangedBuilding,
          ),
        ),
      ],
    );
  }
}
