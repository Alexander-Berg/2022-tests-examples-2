#pragma once

#include <gmock/gmock.h>
#include <clients/driver-orders/client_mock_base.hpp>

namespace test::mocks {

namespace driver_orders = clients::driver_orders;

class DriverOrdersClient final : public clients::driver_orders::ClientMockBase {
 public:
  MOCK_METHOD(driver_orders::v1_parks_orders_list::post::Response,
              V1ParksOrdersList,
              (const driver_orders::v1_parks_orders_list::post::Request&,
               const driver_orders::CommandControl& command_control),
              (const, override));
};

}  // namespace test::mocks
