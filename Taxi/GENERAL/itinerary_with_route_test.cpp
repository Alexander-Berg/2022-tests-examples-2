#include "itinerary_with_route.hpp"

#include <userver/utest/utest.hpp>

using namespace driver_route_watcher::models;
using namespace driver_route_watcher::internal;
using namespace ::geometry::literals;

namespace {
const ::geometry::Position kX = {30.0_lon, 50.0_lat};
const ::geometry::Position kA = {37.5_lon, 53.5_lat};
const ::geometry::Position kB = {38.0_lon, 54.0_lat};
const ::geometry::Position kC = {38.5_lon, 54.5_lat};
const ::geometry::Position kD = {39.0_lon, 55.0_lat};
const ::geometry::Position kE = {39.5_lon, 55.5_lat};

struct PointsWithRoute {
  std::vector<TrackedDestinationPoint> points;
  Route route;
};

TrackedDestinationPoint MakeTestTrackedDestinationPoint(
    const ::geometry::Position& destination, bool is_connected) {
  return TrackedDestinationPoint{DestinationPoint{destination},
                                 ServiceId("some_service_id"),
                                 is_connected,
                                 std::nullopt,
                                 1.0,
                                 false,
                                 std::nullopt,
                                 std::nullopt,
                                 "some_meta_info"};
}

PointsWithRoute MakeTestData(
    const std::vector<::geometry::Position>& destinations,
    const std::vector<bool>& connections) {
  UINVARIANT(destinations.size() == connections.size(),
             "Sizes must be the same");

  PointsWithRoute result;

  result.points.reserve(destinations.size());

  // make points
  for (size_t i = 0; i < destinations.size(); ++i) {
    auto point = TrackedDestinationPoint{DestinationPoint{destinations[i]},
                                         ServiceId("some_service_id"),
                                         connections[i],
                                         std::nullopt,
                                         1.0,
                                         false,
                                         std::nullopt,
                                         std::nullopt,
                                         "some_meta_info"};
    result.points.push_back(std::move(point));
  }

  // make route
  auto& path = result.route.path;
  auto& legs = result.route.legs;
  std::chrono::seconds current_time{0};
  ::geometry::Distance current_dist{0};
  for (size_t i = 0; i < destinations.size(); ++i) {
    // fill legs
    if (i == 0) {
      legs.push_back({0});
    } else {
      legs.push_back({path.size()});
    }
    // fill path
    double current_lat = destinations[i].latitude.GetUnderlying();
    double current_lon = destinations[i].longitude.GetUnderlying();
    double prev_lat;
    double prev_lon;
    if (i > 0) {
      prev_lat = destinations[i - 1].latitude.GetUnderlying();
      prev_lon = destinations[i - 1].longitude.GetUnderlying();
    } else {
      prev_lat = kX.latitude.GetUnderlying();
      prev_lon = kX.longitude.GetUnderlying();
    }
    double delt_lat = (current_lat - prev_lat) / 10;
    double delt_lon = (current_lon - prev_lon) / 10;
    for (size_t j = 0; j < 10; ++j) {
      path.push_back(
          {{::geometry::Latitude::from_value(prev_lat + delt_lat * j),
            ::geometry::Longitude::from_value(prev_lon + delt_lon * j)},
           current_time,
           current_dist});
      current_time += std::chrono::seconds{10};  // +10 sec
      current_dist += 100 * ::geometry::meter;   // +100 m
    }
  }
  path.push_back({destinations.back(), current_time, current_dist});
  // fill rout info
  result.route.info.time = path.back().time_since_ride_start;
  result.route.info.distance = path.back().distance_since_ride_start;

  return result;
}

std::vector<routing_base::RoutePath::Path> MakePathsForLegs(
    const std::vector<::geometry::Position>& destinations) {
  std::vector<routing_base::RoutePath::Path> result;
  result.reserve(destinations.size());

  std::chrono::seconds current_time{0};
  ::geometry::Distance current_dist{0};
  for (size_t i = 0; i < destinations.size(); ++i) {
    double current_lat = destinations[i].latitude.GetUnderlying();
    double current_lon = destinations[i].longitude.GetUnderlying();
    double prev_lat;
    double prev_lon;
    if (i > 0) {
      prev_lat = destinations[i - 1].latitude.GetUnderlying();
      prev_lon = destinations[i - 1].longitude.GetUnderlying();
    } else {
      prev_lat = kX.latitude.GetUnderlying();
      prev_lon = kX.longitude.GetUnderlying();
    }
    double delt_lat = (current_lat - prev_lat) / 10;
    double delt_lon = (current_lon - prev_lon) / 10;
    routing_base::RoutePath::Path path;
    for (size_t j = 0; j < 11; ++j) {
      path.push_back(
          {{::geometry::Latitude::from_value(prev_lat + delt_lat * j),
            ::geometry::Longitude::from_value(prev_lon + delt_lon * j)},
           current_time,
           current_dist});
      if (j != 10) {
        current_time += std::chrono::seconds{10};  // +10 sec
        current_dist += 100 * ::geometry::meter;   // +100 m}
      }
    }

    result.push_back(std::move(path));
  }

  return result;
}

bool IsEqual(const TrackedDestinationPoint& lhs,
             const TrackedDestinationPoint& rhs) {
  return lhs.GetPosition() == rhs.GetPosition() &&
         lhs.GetServiceId() == rhs.GetServiceId() &&
         lhs.GetPointId() == rhs.GetPointId() &&
         lhs.GetOrderId() == rhs.GetOrderId() &&
         lhs.GetEtaMultiplier() == rhs.GetEtaMultiplier() &&
         lhs.GetWaitTime() == rhs.GetWaitTime() &&
         lhs.GetParkTime() == rhs.GetParkTime() &&
         lhs.GetTimestamp() == rhs.GetTimestamp() &&
         lhs.GetType() == rhs.GetType() &&
         lhs.AreTollRoadsAllowed() == rhs.AreTollRoadsAllowed() &&
         lhs.IsConnected() == rhs.IsConnected() &&
         lhs.GetOrderNearestZone() == rhs.GetOrderNearestZone() &&
         lhs.GetOrderCountry() == rhs.GetOrderCountry() &&
         lhs.GetMetainfo() == rhs.GetMetainfo();
}
}  // namespace

UTEST(itinerary_with_route, base_test) {
  // empty vector
  // ASSERT_ANY_THROW(Itinerary(std::vector<TrackedDestinationPoint>{}),
  // Route{});

  // A, A-B-C-D, D-E
  PointsWithRoute test_data =
      MakeTestData({kA, kB, kC, kD, kE}, {false, false, true, true, false});
  std::vector<routing_base::RoutePath::Path> paths_for_legs =
      MakePathsForLegs({kA, kB, kC, kD, kE});

  auto itinerary_with_route =
      ItineraryWithRoute{Itinerary{test_data.points}, test_data.route};

  EXPECT_EQ(itinerary_with_route.size(), 5);
  for (size_t i = 0; i < itinerary_with_route.size(); ++i) {
    // check itinerary
    EXPECT_TRUE(IsEqual(itinerary_with_route[i], test_data.points[i]));
    // check route views
    EXPECT_EQ(itinerary_with_route[i].route_to_point.size(),
              paths_for_legs[i].size());
    for (size_t j = 0; j < itinerary_with_route[i].route_to_point.size(); ++j) {
      EXPECT_EQ(itinerary_with_route[i].route_to_point[j],
                paths_for_legs[i][j]);
    }
  }

  const auto& connected_segments =
      itinerary_with_route.GetConnectedSegmentsView();

  EXPECT_EQ(itinerary_with_route.ConnectedSegmentsCount(), 3);
  ASSERT_EQ(connected_segments.size(), 3);

  // the first connected segment is A
  EXPECT_EQ(connected_segments[0].size(), 1);
  for (size_t i = 0; i < connected_segments[0].size(); ++i) {
    // check itinerary
    EXPECT_TRUE(
        IsEqual(connected_segments[0][i], *(test_data.points.begin() + i)));
    // check route views
    EXPECT_EQ(itinerary_with_route[0].route_to_point.size(),
              paths_for_legs[0].size());
    for (size_t j = 0; j < itinerary_with_route[i].route_to_point.size(); ++j) {
      EXPECT_EQ(connected_segments[0][i].route_to_point[j],
                paths_for_legs[0][j]);
    }
  }

  // the second connected segment is A-B-C-D
  EXPECT_EQ(connected_segments[1].size(), 4);
  for (size_t i = 0; i < connected_segments[1].size(); ++i) {
    // check itinerary
    EXPECT_TRUE(
        IsEqual(connected_segments[1][i], *(test_data.points.begin() + i)));
    // check route views
  }

  // the third connected segment is D-E
  EXPECT_EQ(connected_segments[2].size(), 2);
  for (size_t i = 0; i < connected_segments[2].size(); ++i) {
    // check itinerary
    EXPECT_TRUE(
        IsEqual(connected_segments[2][i], *(test_data.points.begin() + 3 + i)));
    // check route views
  }
}

UTEST(itinerary_with_route, move_test) {
  std::vector<::geometry::Position> tracked_points;
  std::vector<bool> connections;
  ::geometry::Latitude start_lat = 10.0_lat;
  ::geometry::Longitude start_lon = 20.0_lon;
  for (size_t i = 0; i < 10; ++i) {
    for (size_t j = 0; j < 10; ++j) {
      ::geometry::Position pos{
          ::geometry::Latitude::from_value(start_lat.GetUnderlying() + 1.0 * i +
                                           0.1 * j),
          ::geometry::Longitude::from_value(start_lon.GetUnderlying() +
                                            1.0 * i + 0.1 * j)};
      tracked_points.push_back(pos);
      connections.push_back(std::rand() % 2);
    }
  }

  PointsWithRoute test_data =
      MakeTestData(tracked_points, std::move(connections));
  std::vector<routing_base::RoutePath::Path> paths_for_legs =
      MakePathsForLegs(std::move(tracked_points));

  // move constructor
  {
    auto itinerary_with_route_ptr = std::make_unique<ItineraryWithRoute>(
        Itinerary{test_data.points}, test_data.route);
    auto itinerary_with_route{std::move(*itinerary_with_route_ptr)};
    itinerary_with_route_ptr = nullptr;

    ASSERT_EQ(itinerary_with_route.size(), test_data.points.size());
    for (size_t i = 0; i < itinerary_with_route.size(); ++i) {
      // check itinerary
      EXPECT_TRUE(IsEqual(itinerary_with_route[i], test_data.points[i]));
      // check route views
      EXPECT_EQ(itinerary_with_route[i].route_to_point.size(),
                paths_for_legs[i].size());
      for (size_t j = 0; j < itinerary_with_route[i].route_to_point.size();
           ++j) {
        EXPECT_EQ(itinerary_with_route[i].route_to_point[j],
                  paths_for_legs[i][j]);
      }
    }

    std::vector<ItineraryWithRoute::ItineraryPoint> exclude_optimization;
    std::vector<clients::routing::RoutePath> paths;
    const auto& connected_segments =
        itinerary_with_route.GetConnectedSegmentsView();
    for (size_t i = 0; i < itinerary_with_route.ConnectedSegmentsCount(); ++i) {
      for (size_t j = 0; j < connected_segments[i].size(); ++j) {
        exclude_optimization.push_back(connected_segments[i][j]);
        paths.push_back(connected_segments[i].CreateSegmentPath());
      }
    }
    EXPECT_TRUE(exclude_optimization.size() > 0);
    EXPECT_TRUE(paths.size() > 0);
  }

  // move assigned operator
  {
    auto itinerary_with_route_ptr = std::make_unique<ItineraryWithRoute>(
        Itinerary{test_data.points}, test_data.route);
    Route route;
    route.path = MakePathsForLegs({kA})[0];
    route.legs = {{0}};
    ItineraryWithRoute itinerary_with_route{
        Itinerary{std::vector<TrackedDestinationPoint>{
            MakeTestTrackedDestinationPoint(kA, false)}},
        std::move(route)};
    itinerary_with_route = {std::move(*itinerary_with_route_ptr)};
    itinerary_with_route_ptr = nullptr;

    ASSERT_EQ(itinerary_with_route.size(), test_data.points.size());
    for (size_t i = 0; i < itinerary_with_route.size(); ++i) {
      // check itinerary
      EXPECT_TRUE(IsEqual(itinerary_with_route[i], test_data.points[i]));
      // check route views
      EXPECT_EQ(itinerary_with_route[i].route_to_point.size(),
                paths_for_legs[i].size());
      for (size_t j = 0; j < itinerary_with_route[i].route_to_point.size();
           ++j) {
        EXPECT_EQ(itinerary_with_route[i].route_to_point[j],
                  paths_for_legs[i][j]);
      }
    }

    std::vector<ItineraryWithRoute::ItineraryPoint> exclude_optimization;
    std::vector<clients::routing::RoutePath> paths;
    const auto& connected_segments =
        itinerary_with_route.GetConnectedSegmentsView();
    for (size_t i = 0; i < itinerary_with_route.ConnectedSegmentsCount(); ++i) {
      for (size_t j = 0; j < connected_segments[i].size(); ++j) {
        exclude_optimization.push_back(connected_segments[i][j]);
      }
      paths.push_back(connected_segments[i].CreateSegmentPath());
    }
    EXPECT_TRUE(exclude_optimization.size() > 0);
    EXPECT_TRUE(paths.size() > 0);
  }
}
