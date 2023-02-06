#include <gtest/gtest.h>

#include <ml/route_time/api/v1.hpp>

TEST(RouteTimeV1, predict) {
  namespace api = ml::route_time::api::v1;
  std::vector<api::RouteItem> route = {
      api::RouteItem{0, 1, "Zone1"},
      api::RouteItem{1, 2, "Zone2"},
  };
  ASSERT_NEAR(api::Predict(route, {0.9, 1.1}), 0.9165, 1e-4);
  ASSERT_NEAR(api::Predict(route, {0.95, 1.1}), 0.9624, 1e-4);
  ASSERT_NEAR(api::Predict(route, {1.0, 1.1}), 1.0082, 1e-4);
}
