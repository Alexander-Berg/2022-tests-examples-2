#include <gtest/gtest.h>

#include <userver/utils/datetime.hpp>
#include "helpers/driver_profiles.hpp"

#include <fmt/format.h>

clients::driver_profiles::DriverProfilesItem CreateDriverProfile(
    const std::string& park_driver_profile_id, const std::string& work_status,
    const std::string& created_date) {
  auto profile = clients::driver_profiles::DriverProfilesItem{};
  profile.park_driver_profile_id = park_driver_profile_id;
  profile.data = ::clients::driver_profiles::DriverProfilesItemData{};
  profile.data->work_status = work_status;
  profile.data->created_date = created_date;

  return profile;
}

TEST(GetActualParkDriverProfileId, EmptyResult) {
  clients::driver_profiles::v1_courier_profiles_retrieve_by_eats_id::post::
      Response200CourierbyeatsidA profile_info;
  profile_info.profiles = {};

  auto result =
      eats_performer_subventions::helpers::GetActualParkDriverProfileId(
          profile_info);

  ASSERT_EQ(std::nullopt, result);
}

TEST(GetActualParkDriverProfileId, OneProfileInProfileInfo) {
  clients::driver_profiles::v1_courier_profiles_retrieve_by_eats_id::post::
      Response200CourierbyeatsidA profile_info;
  profile_info.profiles = {CreateDriverProfile(
      "park_driver_profile_id_1", "working", "2021-01-15T06:56:07.000")};

  auto result =
      eats_performer_subventions::helpers::GetActualParkDriverProfileId(
          profile_info);

  ASSERT_EQ("park_driver_profile_id_1", result);
}

TEST(GetActualParkDriverProfileId, OneWorkingOtherNot) {
  clients::driver_profiles::v1_courier_profiles_retrieve_by_eats_id::post::
      Response200CourierbyeatsidA profile_info;
  profile_info.profiles = {
      CreateDriverProfile("park_driver_profile_id_1", "lost",
                          "2021-01-15T06:56:07.000"),
      CreateDriverProfile("park_driver_profile_id_2", "working",
                          "2020-01-15T06:56:07.000"),
      CreateDriverProfile("park_driver_profile_id_3", "lost",
                          "2021-01-15T06:56:07.000"),
      CreateDriverProfile("park_driver_profile_id_4", "lost",
                          "2022-01-15T06:56:07.000"),
  };

  auto result =
      eats_performer_subventions::helpers::GetActualParkDriverProfileId(
          profile_info);

  ASSERT_EQ("park_driver_profile_id_2", result);
}

TEST(GetActualParkDriverProfileId, AllWorkingCheckingByCreatedDate) {
  clients::driver_profiles::v1_courier_profiles_retrieve_by_eats_id::post::
      Response200CourierbyeatsidA profile_info;
  profile_info.profiles = {
      CreateDriverProfile("park_driver_profile_id_1", "working",
                          "2021-01-15T06:56:07.000"),
      CreateDriverProfile("park_driver_profile_id_2", "working",
                          "2020-01-15T06:56:07.000"),
      CreateDriverProfile("park_driver_profile_id_3", "working",
                          "2022-01-15T06:56:07.000"),
      CreateDriverProfile("park_driver_profile_id_4", "working",
                          "2021-01-15T06:56:07.000"),
  };

  auto result =
      eats_performer_subventions::helpers::GetActualParkDriverProfileId(
          profile_info);

  ASSERT_EQ("park_driver_profile_id_3", result);
}
