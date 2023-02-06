#include <clients/routing/test/router_mock.hpp>

#include <userver/utest/utest.hpp>

namespace clients::routing {

// Here we test that our RouterMock is actually working

TEST(RouterMockTest, Basic) {
  auto mock_object =
      std::make_unique<::testing::NiceMock<clients::routing::RouterMock>>(
          RouterVehicleType::kVehicleCar);

  mock_object->EnableDefaults();
  EXPECT_TRUE(mock_object->IsEnabled());
  EXPECT_TRUE(mock_object->HasFeatures(RouterFeatures::kMatrixInfo));
}

}  // namespace clients::routing
