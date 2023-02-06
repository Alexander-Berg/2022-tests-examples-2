#include <gtest/gtest.h>
#include <userver/formats/json/serialize_container.hpp>
#include <userver/formats/json/value_builder.hpp>
#include <utest/routing/mock_config_test.hpp>

#include <vendors/fallback/router_fallback.hpp>
#include "clients/routing/router_types.hpp"

namespace {

static const double kAbsError = 0.1;
static const double kAbsPosError = 0.000001;

}  // namespace

using clients::routing::RouterVehicleType;

TEST(RouterFallbackTest, Route) {
  const auto config_storage = clients::routing::utest::CreateRouterConfig();
  clients::routing::RouterFallback router(config_storage.GetSource(),
                                          RouterVehicleType::kVehicleCar);

  using namespace ::geometry::literals;
  clients::routing::Path path = {{37.0_lon, 55.0_lat},
                                 {37.1_lon, 55.0_lat},
                                 {37.1_lon, 55.1_lat},
                                 {37.0_lon, 55.0_lat}};

  const auto result = *router.FetchRouteInfo(path, std::nullopt);

  EXPECT_NEAR(30312.2, result.distance->value(), kAbsError);
  EXPECT_NEAR(4364, result.time->count(), kAbsError);
}

TEST(RouterFallbackTest, PedestrianRoute) {
  const auto config_storage = clients::routing::utest::CreateRouterConfig();
  clients::routing::RouterFallback router(
      config_storage.GetSource(), RouterVehicleType::kVehiclePedestrian);

  using namespace ::geometry::literals;
  clients::routing::Path path = {{37.0_lon, 55.0_lat},
                                 {37.1_lon, 55.0_lat},
                                 {37.1_lon, 55.1_lat},
                                 {37.0_lon, 55.0_lat}};

  const auto result = *router.FetchRouteInfo(path, std::nullopt);

  EXPECT_NEAR(30312.2, result.distance->value(), kAbsError);
  EXPECT_NEAR(21824, result.time->count(), kAbsError);
}

TEST(RouterFallbackTest, BicycleRoute) {
  const auto config_storage = clients::routing::utest::CreateRouterConfig();
  clients::routing::RouterFallback router(config_storage.GetSource(),
                                          RouterVehicleType::kVehicleBicycle);

  using namespace ::geometry::literals;
  clients::routing::Path path = {{37.0_lon, 55.0_lat},
                                 {37.1_lon, 55.0_lat},
                                 {37.1_lon, 55.1_lat},
                                 {37.0_lon, 55.0_lat}};

  const auto result = *router.FetchRouteInfo(path, std::nullopt);

  EXPECT_NEAR(30312.2, result.distance->value(), kAbsError);
  EXPECT_NEAR(7274, result.time->count(), kAbsError);
}

TEST(RouterFallbackTest, RouteWithPath) {
  const auto config_storage = clients::routing::utest::CreateRouterConfig();
  clients::routing::RouterFallback router(config_storage.GetSource(),
                                          RouterVehicleType::kVehicleTruck);

  using namespace ::geometry::literals;
  clients::routing::Path path = {{37.0_lon, 55.0_lat},
                                 {37.1_lon, 55.0_lat},
                                 {37.1_lon, 55.1_lat},
                                 {37.0_lon, 55.0_lat}};

  const auto result = *router.FetchRoutePath(path, std::nullopt);

  EXPECT_NEAR(30312.2, result.info.distance->value(), kAbsError);
  EXPECT_NEAR(4364, result.info.time->count(), kAbsError);

  const auto& route = result.path;

  ASSERT_EQ(4u, route.size());

  EXPECT_NEAR(55.0, route[0].latitude.value(), kAbsPosError);
  EXPECT_NEAR(37.0, route[0].longitude.value(), kAbsPosError);
  EXPECT_NEAR(0.0, route[0].distance_since_ride_start.value(), kAbsError);
  EXPECT_NEAR(0.0, route[0].time_since_ride_start.count(), kAbsError);

  EXPECT_NEAR(55.0, route[1].latitude.value(), kAbsPosError);
  EXPECT_NEAR(37.1, route[1].longitude.value(), kAbsPosError);
  EXPECT_NEAR(6377.9, route[1].distance_since_ride_start.value(), kAbsError);
  EXPECT_NEAR(918, route[1].time_since_ride_start.count(), kAbsError);

  EXPECT_NEAR(55.1, route[2].latitude.value(), kAbsPosError);
  EXPECT_NEAR(37.1, route[2].longitude.value(), kAbsPosError);
  EXPECT_NEAR(17497.4, route[2].distance_since_ride_start.value(), kAbsError);
  EXPECT_NEAR(2519, route[2].time_since_ride_start.count(), kAbsError);

  EXPECT_NEAR(55.0, route[3].latitude.value(), kAbsPosError);
  EXPECT_NEAR(37.0, route[3].longitude.value(), kAbsPosError);
  EXPECT_NEAR(30312.2, route[3].distance_since_ride_start.value(), kAbsError);
  EXPECT_NEAR(4364, route[3].time_since_ride_start.count(), kAbsError);
}

TEST(RouterFallbackTest, Matrix) {
  const auto config_storage = clients::routing::utest::CreateRouterConfig();
  clients::routing::RouterFallback router(config_storage.GetSource(),
                                          RouterVehicleType::kVehicleTaxi);

  using namespace ::geometry::literals;
  std::vector<clients::routing::Point> srcs = {{37.0_lon, 55.0_lat},
                                               {37.1_lon, 55.0_lat}};
  std::vector<clients::routing::DirectionOpt> srcs_dirs = {
      std::nullopt, geometry::Azimuth::from_value(15)};
  std::vector<clients::routing::Point> dsts = {{37.1_lon, 55.1_lat},
                                               {37.0_lon, 55.0_lat}};
  std::vector<clients::routing::DirectionOpt> dsts_dirs = {
      std::nullopt, geometry::Azimuth::from_value(15)};

  const auto result = *router.FetchMatrixInfo(srcs, srcs_dirs, dsts, dsts_dirs);
  EXPECT_EQ(result.size(), 4);
  std::vector<double> dists = {12814.814452226934, 0, 11119.507973463469,
                               6377.8872142089631};
  for (size_t i = 0; i < 2; ++i) {
    for (size_t j = 0; j < 2; ++j) {
      EXPECT_EQ(i, result[i][j].src_point_idx);
      EXPECT_EQ(j, result[i][j].dst_point_idx);

      EXPECT_NEAR(dists[i * 2 + j], result[i][j].distance->value(), kAbsError);
    }
  }
}
