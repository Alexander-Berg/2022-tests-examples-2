#include <gtest/gtest.h>

#include "output_entry.hpp"

#include <internal/unittest_utils/test_utils.hpp>

using driver_route_watcher::test_utils::MakeDestination;

TEST(fbs_output_entry, base) {
  using driver_route_watcher::models::DriverPosition;
  using driver_route_watcher::models::Position;
  using driver_route_watcher::models::TrackingData;
  using driver_route_watcher::models::TrackingType;
  using ::geometry::lat;
  using ::geometry::lon;

  const auto now = utils::datetime::Now();
  auto destination = MakeDestination(Position{11 * lat, 22 * lon}, now);
  destination.eta_multiplier = 0.5;
  destination.order_nearest_zone =
      driver_route_watcher::models::ZoneId("Mordor");
  destination.order_country = driver_route_watcher::models::Country("Gondor");
  const auto route_id = driver_route_watcher::models::RouteId("routeid123_42");
  const auto position = Position{33 * lat, 44 * lon};
  const auto raw_position = Position{55 * lat, 66 * lon};
  const auto time_left = std::chrono::seconds(42);
  const auto distance_left = 100500 * ::geometry::meter;
  const auto tracking_type = TrackingType::kLinearFallback;
  const auto direction = ::geometry::Azimuth::from_value(280);
  const auto tracking_since = now;
  const auto output_updated = now;
  const auto raw_direction =
      ::std::make_optional(::geometry::Azimuth::from_value(137));
  const auto route_segment_id = 142;
  const auto raw_driver_position = DriverPosition(
      raw_position, std::nullopt, std::nullopt, raw_direction, tracking_since,
      driver_route_watcher::models::TransportType::kPedestrian,
      driver_route_watcher::models::Adjusted::kNo);
  const auto orig = [&]() {
    auto tracking_data = TrackingData(
        destination, position,
        {
            {time_left, distance_left, tracking_type},
            {time_left * 2, distance_left * 2, tracking_type},
        },
        {}, direction, raw_driver_position, {}, tracking_type, tracking_since,
        route_segment_id, route_id, output_updated);
    return tracking_data;
  }();
  const auto fbs = driver_route_watcher::internal::ToFlatbuffers(orig);
  const auto entry = driver_route_watcher::internal::ToOutputEntry(fbs);
  ASSERT_TRUE(::geometry::AreClosePositions(orig.GetAdjustedPosition(),
                                            entry.GetAdjustedPosition()));
  ASSERT_TRUE(::geometry::AreClosePositions(orig.GetRawDriverPosition(),
                                            entry.GetRawDriverPosition()));
  ASSERT_TRUE(::geometry::AreClosePositions(
      orig.destination.ExpressDestinationAsPosition(),
      entry.destination.ExpressDestinationAsPosition()));
  ASSERT_EQ(orig.destination.service_id, entry.destination.service_id);
  ASSERT_EQ(orig.destination.metainfo, entry.destination.metainfo);
  ASSERT_EQ(orig.destination.order_id, entry.destination.order_id);
  ASSERT_EQ(orig.destination.order_nearest_zone,
            entry.destination.order_nearest_zone);
  ASSERT_EQ(orig.destination.order_country, entry.destination.order_country);
  ASSERT_EQ(orig.destination.transport_type, entry.destination.transport_type);
  ASSERT_EQ(orig.destination.all_points.size(),
            entry.destination.all_points.size());
  ASSERT_EQ(orig.destination.all_points.front(),
            entry.destination.all_points.front());
  ASSERT_EQ(orig.destination.eta_multiplier, entry.destination.eta_multiplier);
  ASSERT_EQ(orig.GetEta().distance_left, entry.GetEta().distance_left);
  ASSERT_EQ(orig.GetEta().time_left, entry.GetEta().time_left);
  ASSERT_EQ(orig.GetEta().tracking_type, entry.GetEta().tracking_type);
  ASSERT_EQ(orig.GetEtas(), entry.GetEtas());
  ASSERT_EQ(orig.GetDirection(), entry.GetDirection());
  ASSERT_LE(orig.GetTrackingSince() - entry.GetTrackingSince(),
            std::chrono::seconds(1));
  ASSERT_LE(orig.destination.timestamp - entry.destination.timestamp,
            std::chrono::seconds(1));
  ASSERT_TRUE(entry.GetSegmentId());
  ASSERT_EQ(orig.GetSegmentId(), entry.GetSegmentId());
  ASSERT_EQ(orig.GetRawDriverPosition().transport_type,
            entry.GetRawDriverPosition().transport_type);
  ASSERT_EQ(orig.GetRouteId(), entry.GetRouteId());

  // If failed update test (add checks for new fields)
  ASSERT_EQ(328, fbs.size());
}
