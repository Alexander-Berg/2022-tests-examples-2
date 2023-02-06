import 'package:state_notifier/state_notifier.dart';

import 'address.dart';
import 'address_page_state.dart';

class AddressPageStateHolder extends StateNotifier<AddressPageState> {
  AddressPageStateHolder([Address? address])
      : super(
          address == null
              ? const AddressPageState()
              : AddressPageState(
                  city: address.city,
                  street: address.street,
                  house: address.house,
                  corpus: address.corpus,
                  building: address.building,
                ),
        );

  void onChangedCity(String city) {
    state = state.copyWith(city: city);
  }

  void onChangedStreet(String street) {
    state = state.copyWith(street: street);
  }

  void onChangedHouse(String house) {
    state = state.copyWith(house: house);
  }

  void onChangedCorpus(String corpus) {
    state = state.copyWith(corpus: corpus);
  }

  void onChangedBuilding(String building) {
    state = state.copyWith(building: building);
  }

  Address get address => Address(
        city: state.city ?? '',
        street: state.street ?? '',
        house: state.house ?? '',
        corpus: state.corpus ?? '',
        building: state.building ?? '',
      );
}
