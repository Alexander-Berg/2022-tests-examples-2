#include <gmock/gmock.h>
#include <gtest/gtest.h>
#include <userver/utest/utest.hpp>

#include <clients/routing/exceptions.hpp>
#include <clients/routing/router_selector.hpp>
#include <clients/routing/test/router_selector_mock.hpp>
#include <contractor-router/contractor_router.hpp>

namespace contractor_router::test {

class ContractorRouterTest : public ::testing::Test {};

struct Base {
  virtual void f() {}
};

struct Derived : Base {
  MOCK_METHOD(void, f, (), ());
};

UTEST_F(ContractorRouterTest, SelectCarRouter) {
  using ::testing::_;

  auto mock_selector = clients::routing::RouterSelectorMock();
  auto contractor_router = ContractorRouter(mock_selector);

  Contractor car;
  car.tags = {ContractorRouter::Tag::kCar};
  car.source_position = {55.74 * geometry::lat, 37.5 * geometry::lon};

  const geometry::Position destination = {55.732772 * ::geometry::lat,
                                          37.615464 * ::geometry::lon};

  EXPECT_CALL(mock_selector, GetCarRouter(_, _, _)).Times(1);
  try {
    contractor_router.GetRoutes({car}, destination);
  } catch (clients::routing::NoRouterFeatureAvailableError) {
    // ok
  }
}

UTEST_F(ContractorRouterTest, SelectPedestrianRouter) {
  using ::testing::_;

  auto mock_selector = clients::routing::RouterSelectorMock();
  auto contractor_router = ContractorRouter(mock_selector);

  Contractor pedestrian;
  pedestrian.tags = {ContractorRouter::Tag::kPedestrian};
  pedestrian.source_position = {55.74 * geometry::lat, 37.5 * geometry::lon};

  const geometry::Position destination = {55.732772 * ::geometry::lat,
                                          37.615464 * ::geometry::lon};

  EXPECT_CALL(mock_selector, GetPedestrianRouter(_, _, _)).Times(1);
  try {
    contractor_router.GetRoutes({pedestrian}, destination);
  } catch (clients::routing::NoRouterFeatureAvailableError) {
    // ok
  }
}

}  // namespace contractor_router::test
