#pragma once

#include <gmock/gmock.h>
#include <clients/driver-profiles/client_mock_base.hpp>

namespace test::mocks {

namespace driver_profiles = clients::driver_profiles;

class DriverProfilesClient final
    : public clients::driver_profiles::ClientMockBase {
 public:
  MOCK_METHOD(
      driver_profiles::v1_driver_app_profiles_retrieve::post::Response,
      V1DriverAppProfilesRetrieve,
      (const driver_profiles::v1_driver_app_profiles_retrieve::post::Request&,
       const driver_profiles::CommandControl& command_control),
      (const, override));
  MOCK_METHOD(
      driver_profiles::v1_driver_profiles_retrieve::post::Response,
      V1DriverProfilesRetrieve,
      (const driver_profiles::v1_driver_profiles_retrieve::post::Request&,
       const driver_profiles::CommandControl& command_control),
      (const, override));
};

}  // namespace test::mocks
