#include "make_etas_from_route.hpp"

#include "internal/unittest_utils/test_utils.hpp"

#include <userver/utest/utest.hpp>

namespace {
using TrackingData = driver_route_watcher::models::TrackingData;
using Destination = driver_route_watcher::models::Destination;
using Eta = driver_route_watcher::models::Eta;
using TimePoint = driver_route_watcher::models::TimePoint;
using TrackingType = driver_route_watcher::models::TrackingType;
using ServiceId = driver_route_watcher::models::ServiceId;
using RouteId = driver_route_watcher::models::RouteId;
using Route = driver_route_watcher::models::Route;

using driver_route_watcher::test_utils::MakeDestination;

using Position = ::geometry::Position;
using Latitude = ::geometry::Latitude;
using Longitude = ::geometry::Longitude;
using Distance = ::geometry::Distance;

Route MakeRoute() {
  Route ret;
  ret.path.resize(10);
  for (auto i = 0; i < 10; ++i) {
    auto& p = ret.path[i];
    p.time_since_ride_start = std::chrono::seconds(i);
    p.distance_since_ride_start = geometry::Distance::from_value(i);
  }
  ret.legs.push_back({10});
  ret.legs.push_back({10});
  return ret;
}
}  // namespace

TEST(EtasFromRoute, EnsureThereNoOutOfRangeLegs) {
  const auto expected_ouput = std::vector<Eta>();
  const auto input = MakeRoute();
  const auto tracking_type = TrackingType::kRouteTracking;

  const auto output =
      driver_route_watcher::internal::ToEtas(input, tracking_type);
  ASSERT_EQ(output.size(), 2ull);
  ASSERT_EQ(output[0].tracking_type, tracking_type);
  ASSERT_EQ(output[0].distance_left, 9 * geometry::meters);
  ASSERT_EQ(output[0].time_left, std::chrono::seconds(9));

  ASSERT_EQ(output[1].tracking_type, tracking_type);
  ASSERT_EQ(output[1].distance_left, 9 * geometry::meters);
  ASSERT_EQ(output[1].time_left, std::chrono::seconds(9));
}
