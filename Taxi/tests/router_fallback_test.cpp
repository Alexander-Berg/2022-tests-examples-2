#include <gtest/gtest.h>

#include <clients/router_fallback.hpp>
#include <common/mock_handlers_context.hpp>

using namespace clients::routing;

const double kAbsPosError = 0.000001;
const double kAbsError = 0.1;

class RouterFallbackTest : public ::testing::Test, public MockHeadersContext {};

TEST_F(RouterFallbackTest, Route) {
  RouterFallback router;
  clients::routing::Router::path_t path = {
      {37.0, 55.0}, {37.1, 55.0}, {37.1, 55.1}, {37.0, 55.0}};

  std::unique_ptr<clients::routing::RouteInfoEx> result =
      router.RouteEx(path, utils::geometry::kNoDirection, GetContext(), {}, {});

  EXPECT_NEAR(30320.7, result->total_distance, kAbsError);
  EXPECT_NEAR(4366.1, result->total_time, kAbsError);

  auto movement = result->GetMovement();

  ASSERT_EQ(4u, movement.size());

  EXPECT_NEAR(55.0, movement[0].lat(), kAbsPosError);
  EXPECT_NEAR(37.0, movement[0].lon(), kAbsPosError);
  EXPECT_NEAR(0.0, movement[0].distance_since_ride_start, kAbsError);
  EXPECT_NEAR(0.0, movement[0].time_since_ride_start.count(), kAbsError);

  EXPECT_NEAR(55.0, movement[1].lat(), kAbsPosError);
  EXPECT_NEAR(37.1, movement[1].lon(), kAbsPosError);
  EXPECT_NEAR(6379.6, movement[1].distance_since_ride_start, kAbsError);
  EXPECT_NEAR(918.6, movement[1].time_since_ride_start.count(), kAbsError);

  EXPECT_NEAR(movement[2].lat(), 55.1, kAbsPosError);
  EXPECT_NEAR(movement[2].lon(), 37.1, kAbsPosError);
  EXPECT_NEAR(17502.3, movement[2].distance_since_ride_start, kAbsError);
  EXPECT_NEAR(2520.3, movement[2].time_since_ride_start.count(), kAbsError);

  EXPECT_NEAR(55.0, movement[3].lat(), kAbsPosError);
  EXPECT_NEAR(37.0, movement[3].lon(), kAbsPosError);
  EXPECT_NEAR(30320.7, movement[3].distance_since_ride_start, kAbsError);
  EXPECT_NEAR(4366.1, movement[3].time_since_ride_start.count(), kAbsError);
}

TEST_F(RouterFallbackTest, RouteBulk) {
  const auto tp = std::chrono::system_clock::time_point();

  RouterFallback router;
  std::vector<clients::routing::RouteInfo> result = router.RouteBulk(
      {
          clients::routing::TrackPoint{37.0, 55.0, 0, 0, tp},
          clients::routing::TrackPoint{37.1, 55.0, 0, 0, tp},
      },
      {37.1, 55.1}, GetContext(), {});

  ASSERT_EQ(2u, result.size());

  EXPECT_NEAR(12818.4, result[0].total_distance, kAbsError);
  EXPECT_NEAR(1845.8, result[0].total_time, kAbsError);

  EXPECT_NEAR(11122.6, result[1].total_distance, kAbsError);
  EXPECT_NEAR(1601.6, result[1].total_time, kAbsError);
}

TEST_F(RouterFallbackTest, RouteBulkDriverPoint) {
  const auto tp = std::chrono::system_clock::time_point();

  RouterFallback router;
  std::vector<clients::routing::DriverPointEx> from_bulk = {
      clients::routing::DriverPointEx{
          "driver1", {}, clients::routing::TrackPoint{37.0, 55.0, 0, 0, tp}},
      clients::routing::DriverPointEx{
          "driver2",
          {},
          clients::routing::TrackPoint{37.1, 55.0, 0, 0, tp},
      }};
  std::vector<clients::routing::DriverRouteInfo> result =
      router.RouteBulk(from_bulk, {37.1, 55.1}, GetContext(), {});

  ASSERT_EQ(2u, result.size());

  EXPECT_EQ("driver1", result[0].driver_id);
  EXPECT_NEAR(12818.4, result[0].total_distance, kAbsError);
  EXPECT_NEAR(1845.8, result[0].total_time, kAbsError);

  EXPECT_EQ("driver2", result[1].driver_id);
  EXPECT_NEAR(11122.6, result[1].total_distance, kAbsError);
  EXPECT_NEAR(1601.6, result[1].total_time, kAbsError);
}

TEST_F(RouterFallbackTest, RouteBulkDriverPointPairs) {
  const auto tp = std::chrono::system_clock::time_point();

  RouterFallback router;
  std::vector<
      std::pair<clients::routing::DriverPointEx, clients::routing::Point>>
      from_to_bulk = {{clients::routing::DriverPointEx{
                           "driver1",
                           {},
                           clients::routing::TrackPoint{37.0, 55.0, 0, 0, tp}},
                       {37.1, 55.1}},
                      {clients::routing::DriverPointEx{
                           "driver2",
                           {},
                           clients::routing::TrackPoint{37.1, 55.0, 0, 0, tp}},
                       {37.1, 55.1}}};
  std::vector<clients::routing::DriverRouteInfo> result =
      router.RouteBulk(from_to_bulk, GetContext(), {});

  ASSERT_EQ(2u, result.size());

  EXPECT_EQ("driver1", result[0].driver_id);
  EXPECT_NEAR(12818.4, result[0].total_distance, kAbsError);
  EXPECT_NEAR(1845.8, result[0].total_time, kAbsError);

  EXPECT_EQ("driver2", result[1].driver_id);
  EXPECT_NEAR(11122.6, result[1].total_distance, kAbsError);
  EXPECT_NEAR(1601.6, result[1].total_time, kAbsError);
}

TEST_F(RouterFallbackTest, RoutePoints) {
  RouterFallback router;
  clients::routing::Router::path_t path = {
      {37.0, 55.0}, {37.1, 55.0}, {37.1, 55.1}, {37.0, 55.0}};

  auto result = router.GetWaypointInfo(path, GetContext(), {})->Get();

  EXPECT_NEAR(30320.7, result->total_distance, kAbsError);
  EXPECT_NEAR(4366.1, result->total_time, kAbsError);

  auto movement = result->GetWaypoints();

  ASSERT_EQ(4u, movement.size());

  EXPECT_NEAR(55.0, movement[0].lat(), kAbsPosError);
  EXPECT_NEAR(37.0, movement[0].lon(), kAbsPosError);
  EXPECT_NEAR(0.0, movement[0].distance_since_ride_start, kAbsError);
  EXPECT_NEAR(0.0, movement[0].time_since_ride_start.count(), kAbsError);

  EXPECT_NEAR(55.0, movement[1].lat(), kAbsPosError);
  EXPECT_NEAR(37.1, movement[1].lon(), kAbsPosError);
  EXPECT_NEAR(6379.6, movement[1].distance_since_ride_start, kAbsError);
  EXPECT_NEAR(918.6, movement[1].time_since_ride_start.count(), kAbsError);

  EXPECT_NEAR(movement[2].lat(), 55.1, kAbsPosError);
  EXPECT_NEAR(movement[2].lon(), 37.1, kAbsPosError);
  EXPECT_NEAR(17502.3, movement[2].distance_since_ride_start, kAbsError);
  EXPECT_NEAR(2520.3, movement[2].time_since_ride_start.count(), kAbsError);

  EXPECT_NEAR(55.0, movement[3].lat(), kAbsPosError);
  EXPECT_NEAR(37.0, movement[3].lon(), kAbsPosError);
  EXPECT_NEAR(30320.7, movement[3].distance_since_ride_start, kAbsError);
  EXPECT_NEAR(4366.1, movement[3].time_since_ride_start.count(), kAbsError);
}
