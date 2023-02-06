#include "itinerary.hpp"

#include <userver/utest/utest.hpp>

using namespace driver_route_watcher::models;
using namespace driver_route_watcher::internal;
using namespace ::geometry::literals;

namespace {
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

const ::geometry::Position kA = {37.5_lon, 53.5_lat};
const ::geometry::Position kB = {38.0_lon, 54.0_lat};
const ::geometry::Position kC = {38.5_lon, 54.5_lat};
const ::geometry::Position kD = {39.0_lon, 55.0_lat};
const ::geometry::Position kE = {39.5_lon, 55.5_lat};
}  // namespace

UTEST(itinerary, base_test) {
  // empty vector
  // ASSERT_ANY_THROW(Itinerary(std::vector<TrackedDestinationPoint>{}));

  // A, A-B-C-D, D-E
  std::vector<TrackedDestinationPoint> tracked_points{
      MakeTestTrackedDestinationPoint(kA, false),
      MakeTestTrackedDestinationPoint(kB, false),
      MakeTestTrackedDestinationPoint(kC, true),
      MakeTestTrackedDestinationPoint(kD, true),
      MakeTestTrackedDestinationPoint(kE, false)};

  auto itinerary = Itinerary{tracked_points};

  EXPECT_EQ(itinerary.size(), 5);
  for (size_t i = 0; i < itinerary.size(); ++i) {
    EXPECT_TRUE(IsEqual(itinerary[i], tracked_points[i]));
  }

  const auto& connected_segments = itinerary.GetConnectedSegmentsView();

  EXPECT_EQ(itinerary.ConnectedSegmentsCount(), 3);
  ASSERT_EQ(connected_segments.size(), 3);

  // the first connected segment is A
  EXPECT_EQ(connected_segments[0].size(), 1);
  for (size_t i = 0; i < connected_segments[0].size(); ++i) {
    EXPECT_TRUE(
        IsEqual(connected_segments[0][i], *(tracked_points.begin() + i)));
  }

  // the second connected segment is A-B-C-D
  EXPECT_EQ(connected_segments[1].size(), 4);
  for (size_t i = 0; i < connected_segments[1].size(); ++i) {
    EXPECT_TRUE(
        IsEqual(connected_segments[1][i], *(tracked_points.begin() + i)));
  }

  // the third connected segment is D-E
  EXPECT_EQ(connected_segments[2].size(), 2);
  for (size_t i = 0; i < connected_segments[2].size(); ++i) {
    EXPECT_TRUE(
        IsEqual(connected_segments[2][i], *(tracked_points.begin() + 3 + i)));
  }
}

UTEST(itinerary, move_test) {
  std::vector<TrackedDestinationPoint> tracked_points;
  ::geometry::Latitude start_lat = 10.0_lat;
  ::geometry::Longitude start_lon = 20.0_lon;
  for (size_t i = 0; i < 10; ++i) {
    for (size_t j = 0; j < 10; ++j) {
      ::geometry::Position pos{
          ::geometry::Latitude::from_value(start_lat.GetUnderlying() + 1.0 * i +
                                           0.1 * j),
          ::geometry::Longitude::from_value(start_lon.GetUnderlying() +
                                            1.0 * i + 0.1 * j)};
      tracked_points.push_back(
          MakeTestTrackedDestinationPoint(pos, std::rand() % 2));
    }
  }

  // move constructor
  {
    auto itinerary_ptr = std::make_unique<Itinerary>(tracked_points);
    auto itinerary{std::move(*itinerary_ptr)};
    itinerary_ptr = nullptr;

    ASSERT_EQ(itinerary.size(), tracked_points.size());
    for (size_t i = 0; i < itinerary.size(); ++i) {
      EXPECT_TRUE(IsEqual(itinerary[i], tracked_points[i]));
    }

    std::vector<TrackedDestinationPoint> exclude_optimization;
    const auto& connected_segments = itinerary.GetConnectedSegmentsView();
    for (size_t i = 0; i < itinerary.ConnectedSegmentsCount(); ++i) {
      for (size_t j = 0; j < connected_segments[i].size(); ++j) {
        exclude_optimization.push_back(connected_segments[i][j]);
      }
    }
  }

  // move assigned operator
  {
    auto itinerary_ptr = std::make_unique<Itinerary>(tracked_points);
    Itinerary itinerary{std::vector<TrackedDestinationPoint>{
        MakeTestTrackedDestinationPoint(kA, false)}};
    itinerary = {std::move(*itinerary_ptr)};
    itinerary_ptr = nullptr;

    ASSERT_EQ(itinerary.size(), tracked_points.size());
    for (size_t i = 0; i < itinerary.size(); ++i) {
      EXPECT_TRUE(IsEqual(itinerary[i], tracked_points[i]));
    }

    std::vector<TrackedDestinationPoint> exclude_optimization;
    const auto& connected_segments = itinerary.GetConnectedSegmentsView();
    for (size_t i = 0; i < itinerary.ConnectedSegmentsCount(); ++i) {
      for (size_t j = 0; j < connected_segments[i].size(); ++j) {
        exclude_optimization.push_back(connected_segments[i][j]);
      }
    }
  }
}
