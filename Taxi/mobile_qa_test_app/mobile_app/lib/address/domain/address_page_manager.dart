import '../../auth/domain/local_user_manager.dart';
import '../../utils/navigation/navigation_manager.dart';
import 'address_page_state_holder.dart';

class AddressPageManager {
  final AddressPageStateHolder pageStateHolder;
  final LocalUserManager userManager;
  final NavigationManager navigationManager;

  AddressPageManager({
    required this.pageStateHolder,
    required this.userManager,
    required this.navigationManager,
  });

  void onChangedCity(String city) => pageStateHolder.onChangedCity(city);

  void onChangedStreet(String street) =>
      pageStateHolder.onChangedStreet(street);

  void onChangedHouse(String house) => pageStateHolder.onChangedHouse(house);

  void onChangedCorpus(String corpus) => pageStateHolder.onChangedHouse(corpus);

  void onChangedBuilding(String building) =>
      pageStateHolder.onChangedHouse(building);

  Future<void> onNextButtonTapped() async {
    await saveAddress();
    navigationManager.openPaymentPage();
  }

  Future<void> saveAddress() async {
    final address = pageStateHolder.address;
    await userManager.updateAddress(address);
  }
}
