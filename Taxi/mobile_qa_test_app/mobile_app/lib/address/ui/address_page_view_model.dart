import '../../common/validation/models/validation_rules.dart';
import '../domain/address_page_state.dart';

class AddressPageViewModel {
  final AddressPageState pageState;
  final ValidationRules validationRules;

  AddressPageViewModel({
    required this.pageState,
    required this.validationRules,
  });

  bool get isAllDataValid =>
      isCityValid &&
      isStreetValid &&
      isHouseValid &&
      isCorpusValid &&
      isBuildingValid;

  bool get isCityValid => validationRules.isCityValid(pageState.city ?? '');
  bool get isStreetValid =>
      validationRules.isStreetValid(pageState.street ?? '');
  bool get isHouseValid => validationRules.isHouseValid(pageState.house ?? '');
  bool get isCorpusValid =>
      validationRules.isCorpusValid(pageState.corpus ?? '');
  bool get isBuildingValid =>
      validationRules.isBuildingValid(pageState.building ?? '');
}
