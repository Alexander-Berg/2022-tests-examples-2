#include "route_joiner.hpp"

#include "internal/unittest_utils/test_utils.hpp"
#include "types/types.hpp"

#include <gtest/gtest.h>

namespace {
using TrackingData = driver_route_watcher::models::TrackingData;
using Destination = driver_route_watcher::models::Destination;
using Eta = driver_route_watcher::models::Eta;
using TimePoint = driver_route_watcher::models::TimePoint;
using TrackingType = driver_route_watcher::models::TrackingType;
using ServiceId = driver_route_watcher::models::ServiceId;
using RouteId = driver_route_watcher::models::RouteId;
using Route = driver_route_watcher::models::Route;
using DestinationPoint = driver_route_watcher::models::DestinationPoint;

using driver_route_watcher::internal::UniteRoutes;
using driver_route_watcher::test_utils::MakeDestination;

using Position = ::geometry::Position;
using Latitude = ::geometry::Latitude;
using Longitude = ::geometry::Longitude;
using Distance = ::geometry::Distance;
}  // namespace

TEST(UniteRoutes, BaseTest) {
  Route route_1;
  {
    RouteId route_id("route_id_1");
    std::vector<routing_base::RoutePoint> route_path;
    route_path = {
        {Position{Longitude(11), Latitude(21)}, std::chrono::seconds(0),
         Distance(0 * ::geometry::meter)},
        {Position{Longitude(12), Latitude(22)}, std::chrono::seconds(10),
         Distance(200 * ::geometry::meter)},
        {Position{Longitude(13), Latitude(23)}, std::chrono::seconds(20),
         Distance(400 * ::geometry::meter)}};
    routing_base::RouteInfo route_info;
    route_info.distance = Distance(400 * ::geometry::meter);
    route_info.time = std::nullopt;
    route_info.blocked = false;
    route_info.has_toll_roads = true;
    route_info.has_dead_jam = std::nullopt;

    route_1.route_id = route_id.GetUnderlying();
    route_1.request_id = "route_1_request";
    route_1.path = std::move(route_path);
    route_1.info = std::move(route_info);
    route_1.legs = {{0}, {1}};
  }

  Route route_2;
  {
    RouteId route_id("route_id_2");
    std::vector<routing_base::RoutePoint> route_path;
    route_path = {
        {Position{Longitude(13), Latitude(23)}, std::chrono::seconds(0),
         Distance(0 * ::geometry::meter)},
        {Position{Longitude(14), Latitude(24)}, std::chrono::seconds(30),
         Distance(300 * ::geometry::meter)},
        {Position{Longitude(15), Latitude(25)}, std::chrono::seconds(60),
         Distance(600 * ::geometry::meter)}};
    routing_base::RouteInfo route_info;
    route_info.distance = Distance(600 * ::geometry::meter);
    route_info.time = std::chrono::seconds(60);
    route_info.blocked = true;
    route_info.has_toll_roads = std::nullopt;
    route_info.has_dead_jam = false;

    route_2.route_id = route_id.GetUnderlying();
    route_2.request_id = "route_2_request";
    route_2.path = std::move(route_path);
    route_2.info = std::move(route_info);
    route_2.legs = {{0}, {1}};
  }

  Route expected_route;
  expected_route.route_id = "route_id_1";
  expected_route.request_id = "route_1_request";
  expected_route.info.distance = Distance::from_value(1000);
  expected_route.info.time = std::chrono::seconds(80);
  expected_route.info.has_dead_jam = false;
  expected_route.info.blocked = true;
  expected_route.info.has_toll_roads = true;
  expected_route.path = {
      {Position{Longitude(11), Latitude(21)}, std::chrono::seconds(0),
       Distance(0 * ::geometry::meter)},
      {Position{Longitude(12), Latitude(22)}, std::chrono::seconds(10),
       Distance(200 * ::geometry::meter)},
      {Position{Longitude(13), Latitude(23)}, std::chrono::seconds(20),
       Distance(400 * ::geometry::meter)},
      {Position{Longitude(13), Latitude(23)}, std::chrono::seconds(20),
       Distance(400 * ::geometry::meter)},
      {Position{Longitude(14), Latitude(24)}, std::chrono::seconds(50),
       Distance(700 * ::geometry::meter)},
      {Position{Longitude(15), Latitude(25)}, std::chrono::seconds(80),
       Distance(1000 * ::geometry::meter)}};
  expected_route.legs = {{0}, {1}, {3}, {4}};

  auto united_route = UniteRoutes({route_1, route_2});

  EXPECT_EQ(united_route.route_id, expected_route.route_id);
  EXPECT_EQ(united_route.request_id, expected_route.request_id);

  EXPECT_TRUE(united_route.info.distance == expected_route.info.distance);
  EXPECT_TRUE(united_route.info.time == expected_route.info.time);
  EXPECT_TRUE(united_route.info.has_toll_roads ==
              expected_route.info.has_toll_roads);
  EXPECT_TRUE(united_route.info.blocked == expected_route.info.blocked);

  ASSERT_EQ(united_route.path.size(), expected_route.path.size());
  for (size_t i = 0; i < united_route.path.size(); ++i) {
    EXPECT_EQ(united_route.path[i].longitude, expected_route.path[i].longitude);
    EXPECT_EQ(united_route.path[i].latitude, expected_route.path[i].latitude);
    EXPECT_EQ(united_route.path[i].time_since_ride_start,
              expected_route.path[i].time_since_ride_start);
    EXPECT_EQ(united_route.path[i].distance_since_ride_start,
              expected_route.path[i].distance_since_ride_start);
  }

  ASSERT_EQ(united_route.legs.size(), expected_route.legs.size());
  for (size_t i = 0; i < united_route.legs.size(); ++i) {
    EXPECT_EQ(united_route.legs[i].point_index,
              expected_route.legs[i].point_index);
  }
}
