#include <userver/utest/utest.hpp>

#include <utils/get_places_info.hpp>

namespace eats_restapp_places::utils {

TEST(ConvertAddress, return_full_address_for_all_non_empty_components) {
  clients::eats_core::Address core_address;
  core_address.country = "Страна";
  core_address.city = "Город";
  core_address.street = "Улица";
  core_address.building = "11";
  std::string expected_address = "Улица, 11, Город, Страна";
  std::optional<std::string> result_address;
  ConvertAddress(core_address, result_address);
  ASSERT_EQ(result_address.value(), expected_address);
}

TEST(ConvertAddress, return_partial_address_if_some_components_are_empty) {
  clients::eats_core::Address core_address;
  core_address.country = "";
  core_address.city = "Город";
  core_address.street = "";
  core_address.building = "11";
  std::string expected_address = "11, Город";
  std::optional<std::string> result_address;
  ConvertAddress(core_address, result_address);
  ASSERT_EQ(result_address.value(), expected_address);
}

TEST(ConvertAddress, return_empty_address_if_all_components_are_empty) {
  clients::eats_core::Address core_address;
  core_address.country = "";
  core_address.city = "";
  core_address.street = "";
  core_address.building = "";
  std::string expected_address = "";
  std::optional<std::string> result_address;
  ConvertAddress(core_address, result_address);
  ASSERT_EQ(result_address.value(), expected_address);
}

TEST(IsPlaceRequestedToSwitchOn, return_false_if_place_available) {
  PlaceSwitchOnRequest request = {1,
                                  std::chrono::system_clock::from_time_t(100)};

  handlers::PlaceDisabledetails disable_details;
  auto result = IsPlaceRequestedToSwitchOn(true, request,
                                           std::make_optional(disable_details));
  ASSERT_EQ(result, false);
}

TEST(IsPlaceRequestedToSwitchOn, return_true_if_no_disable_details) {
  PlaceSwitchOnRequest request = {1,
                                  std::chrono::system_clock::from_time_t(100)};

  auto result = IsPlaceRequestedToSwitchOn<handlers::PlaceDisabledetails>(
      false, request, std::nullopt);
  ASSERT_EQ(result, true);
}

TEST(IsPlaceRequestedToSwitchOn, return_true_if_place_switched_off_before_db) {
  PlaceSwitchOnRequest request = {1,
                                  std::chrono::system_clock::from_time_t(100)};

  handlers::PlaceDisabledetails disable_details;
  disable_details.disable_at = std::chrono::system_clock::from_time_t(50);
  auto result = IsPlaceRequestedToSwitchOn(false, request,
                                           std::make_optional(disable_details));
  ASSERT_EQ(result, true);
}

TEST(IsPlaceRequestedToSwitchOn, return_false_if_place_switched_off_after_db) {
  PlaceSwitchOnRequest request = {1,
                                  std::chrono::system_clock::from_time_t(100)};

  handlers::PlaceDisabledetails disable_details;
  disable_details.disable_at = std::chrono::system_clock::from_time_t(150);
  auto result = IsPlaceRequestedToSwitchOn(false, request,
                                           std::make_optional(disable_details));
  ASSERT_EQ(result, false);
}

}  // namespace eats_restapp_places::utils
