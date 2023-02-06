#pragma once

#include <gmock/gmock.h>
#include <clients/unique-drivers/client_mock_base.hpp>

namespace test::mocks {

namespace unique_drivers = clients::unique_drivers;

class UniqueDriversClient final
    : public clients::unique_drivers::ClientMockBase {
 public:
  MOCK_METHOD(
      unique_drivers::v1_driver_profiles_retrieve_by_uniques::post::Response,
      V1DriverProfilesRetrieveByUniques,
      (const unique_drivers::v1_driver_profiles_retrieve_by_uniques::post::
           Request&,
       const unique_drivers::CommandControl& command_control),
      (const, override));
};

}  // namespace test::mocks
