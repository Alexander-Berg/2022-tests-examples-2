#include <gtest/gtest.h>
#include <clients/driver-mode-index/client_mock_base.hpp>

#include <helpers/get_drivers.hpp>

#include <fmt/format.h>

namespace dmi = clients::driver_mode_index;

namespace {

class MockDmiClient final : public dmi::ClientMockBase {
  dmi::v1_drivers::post::Response V1Drivers(
      const dmi::v1_drivers::post::Request& request,
      const dmi::CommandControl& /*command_control*/ = {}) const final {
    dmi::v1_drivers::post::Response response;
    if (!request.body.cursor) {
      response.drivers = {"dbid_uuid1", "dbid_uuid2"};
      response.next_cursor = "15";
    } else if (*request.body.cursor == "15") {
      response.drivers = {"dbid_uuid3", "dbid_uuid4"};
      response.next_cursor = "101";
    } else if (*request.body.cursor == "101") {
      response.drivers = {"dbid_uuid5"};
    } else {
      throw std::runtime_error(
          fmt::format("Unexpected cursor value = {}", *request.body.cursor));
    }
    return response;
  }
};

using Driver = driver_id::DriverDbidUndscrUuid;
std::vector<Driver> CreateDrivers(std::vector<std::string>&& drivers) {
  std::vector<Driver> res;
  for (auto&& driver : drivers) {
    res.emplace_back(driver);
  }
  return res;
}

}  // namespace

namespace tests {

TEST(GetDrivers, Test) {
  const auto kExpected = CreateDrivers(
      {"dbid_uuid1", "dbid_uuid2", "dbid_uuid3", "dbid_uuid4", "dbid_uuid5"});
  auto drivers =
      helpers::GetDrivers(MockDmiClient{}, driver_mode::WorkMode("orders"));
  std::sort(begin(drivers), end(drivers));
  ASSERT_EQ(drivers, kExpected);
}

}  // namespace tests
