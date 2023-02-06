#include "building_timelefts_data.hpp"

#include <internal/unittest_utils/test_utils.hpp>
#include "types/types.hpp"

#include <gtest/gtest.h>

namespace {

namespace models = driver_route_watcher::models;

const auto kDriverId = driver_route_watcher::models::DriverId();

TEST(CreateTimelefts, UnknownPoint) {
  std::vector<models::Eta> etas = {
      models::Eta(std::chrono::seconds(4), ::geometry::Distance(0),
                  models::TrackingType::kRouteTracking)};

  std::vector<models::TrackedDestinationPoint> points = {
      models::TrackedDestinationPoint::CreateUknownPoint({}, false, {}, 1,
                                                         false, {}, {}, {}),
  };
  models::TrackingData tracking_data({}, {}, etas, points, {}, {}, {}, {}, {},
                                     {}, {});
  // point is unknown - timeleft isn't Finite
  auto timelefts =
      driver_route_watcher::internal::CreateTimelefts(tracking_data);
  ASSERT_EQ(timelefts.size(), 1);
  EXPECT_FALSE(timelefts[0].destination_position.IsFinite());
  EXPECT_FALSE(timelefts[0].time_distance_left);

  etas = {models::Eta(std::chrono::seconds(4), ::geometry::Distance(0),
                      models::TrackingType::kRouteTracking),
          models::Eta(std::chrono::seconds(4), ::geometry::Distance(0),
                      models::TrackingType::kRouteTracking),
          models::Eta(std::chrono::seconds(0), ::geometry::Distance(0),
                      models::TrackingType::kRouteTracking),
          models::Eta(std::chrono::seconds(0), ::geometry::Distance(0),
                      models::TrackingType::kRouteTracking)};
  points = {
      models::TrackedDestinationPoint({}, {}, false, {}, 1, false, {}, {}, {}),
      models::TrackedDestinationPoint::CreateUknownPoint({}, false, {}, 1,
                                                         false, {}, {}, {}),
      models::TrackedDestinationPoint({}, {}, true, {}, 1, false, {}, {}, {}),
      models::TrackedDestinationPoint({}, {}, true, {}, 1, false, {}, {}, {})};
  tracking_data =
      models::TrackingData({}, {}, etas, points, {}, {}, {}, {}, {}, {}, {});
  // point is unknown - all timelefts after it aren't Finite
  timelefts = driver_route_watcher::internal::CreateTimelefts(tracking_data);
  ASSERT_EQ(timelefts.size(), 4);
  EXPECT_TRUE(timelefts[0].destination_position.IsFinite());
  EXPECT_EQ(timelefts[0].time_distance_left->time, std::chrono::seconds(4));
  EXPECT_EQ(timelefts[0].time_distance_left->distance, ::geometry::Distance(0));
  EXPECT_FALSE(timelefts[1].destination_position.IsFinite());
  EXPECT_FALSE(timelefts[1].time_distance_left);
  EXPECT_TRUE(timelefts[2].destination_position.IsFinite());
  EXPECT_FALSE(timelefts[2].time_distance_left);
  EXPECT_TRUE(timelefts[3].destination_position.IsFinite());
  EXPECT_FALSE(timelefts[3].time_distance_left);

  etas = {models::Eta(std::chrono::seconds(4), ::geometry::Distance(0),
                      models::TrackingType::kUnknownDestination)};
  points = {
      models::TrackedDestinationPoint({}, {}, false, {}, 1, false, {}, {}, {})};
  tracking_data = models::TrackingData::MakeAllPointsRoutingTrackingData(
      {}, etas, points, {}, {}, {}, {}, {}, {}, {});
  // eta is unknow - timeleft isn't Finite
  timelefts = driver_route_watcher::internal::CreateTimelefts(tracking_data);
  ASSERT_EQ(timelefts.size(), 1);
  EXPECT_TRUE(timelefts[0].destination_position.IsFinite());
  EXPECT_FALSE(timelefts[0].time_distance_left);
}

TEST(CreateTimelefts, CorrectFormulaAndZeroTimeleftProcessing) {
  auto etas = {models::Eta(std::chrono::seconds(0), ::geometry::Distance(0),
                           models::TrackingType::kRouteTracking),
               models::Eta(std::chrono::seconds(0), ::geometry::Distance(0),
                           models::TrackingType::kRouteTracking),
               models::Eta(std::chrono::seconds(10), ::geometry::Distance(0),
                           models::TrackingType::kRouteTracking),
               models::Eta(std::chrono::seconds(20), ::geometry::Distance(0),
                           models::TrackingType::kRouteTracking),
               models::Eta(std::chrono::seconds(80), ::geometry::Distance(0),
                           models::TrackingType::kRouteTracking)};
  auto points = {models::TrackedDestinationPoint(
                     models::DestinationPoint({}, {}, std::chrono::seconds(10),
                                              std::chrono::seconds(5), {}, {}),
                     {}, false, {}, 1, false, {}, {}, {}),
                 models::TrackedDestinationPoint(
                     models::DestinationPoint({}, {}, std::chrono::seconds(10),
                                              std::chrono::seconds(5), {}, {}),
                     {}, true, {}, 1, false, {}, {}, {}),
                 models::TrackedDestinationPoint(
                     models::DestinationPoint({}, {}, std::chrono::seconds(20),
                                              std::chrono::seconds(10), {}, {}),
                     {}, true, {}, 2, false, {}, {}, {}),
                 models::TrackedDestinationPoint(
                     models::DestinationPoint({}, {}, std::chrono::seconds(180),
                                              std::chrono::seconds(1), {}, {}),
                     {}, false, {}, 0.5, false, {}, {}, {}),
                 models::TrackedDestinationPoint(
                     models::DestinationPoint({}, {}, std::chrono::seconds(10),
                                              std::chrono::seconds(30), {}, {}),
                     {}, false, {}, 0.9, false, {}, {}, {})};
  auto tracking_data =
      models::TrackingData({}, {}, etas, points, {}, {}, {}, {}, {}, {}, {});
  auto timelefts =
      driver_route_watcher::internal::CreateTimelefts(tracking_data);
  ASSERT_EQ(timelefts.size(), 5);
  // first to points don't use wait and park time
  ASSERT_EQ(timelefts[0].time_distance_left->time, std::chrono::seconds(0));
  ASSERT_EQ(timelefts[1].time_distance_left->time, std::chrono::seconds(0));
  // third point doesn't use wait time from previous zero time_left point
  // it's time = 10 * 2 + 10
  ASSERT_EQ(timelefts[2].time_distance_left->time, std::chrono::seconds(30));
  // fourth point use wait time from previous point
  // it's time = 30 + (20 - 10) * 0.5 + 1 + 20
  ASSERT_EQ(timelefts[3].time_distance_left->time, std::chrono::seconds(56));
  // fourth point use wait time from previous point
  // it's time = 56 + (80 - 20) * 0.9 + 30 + 180
  ASSERT_EQ(timelefts[4].time_distance_left->time, std::chrono::seconds(320));
}

}  // namespace
