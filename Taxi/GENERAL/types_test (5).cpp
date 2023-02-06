#include "types.hpp"
#include <gtest/gtest.h>

namespace models = driver_route_watcher::models;
namespace {

TEST(TrackingData, OldAndNewEtasCorrectFilling) {
  std::vector<models::Eta> etas = {
      models::Eta(std::chrono::seconds(0), ::geometry::Distance(0),
                  models::TrackingType::kRouteTracking),
      models::Eta(std::chrono::seconds(10), ::geometry::Distance(0),
                  models::TrackingType::kRouteTracking)};
  std::vector<models::TrackedDestinationPoint> points = {
      models::TrackedDestinationPoint({}, {}, false, {}, 1, false, {}, {}, {}),
      models::TrackedDestinationPoint({}, {}, true, {}, 1, false, {}, {}, {}),
      models::TrackedDestinationPoint::CreateUknownPoint({}, false, {}, 1,
                                                         false, {}, {}, {}),
      models::TrackedDestinationPoint::CreateUknownPoint({}, false, {}, 1,
                                                         false, {}, {}, {}),
  };
  models::TrackingData tracking_data({}, {}, etas, points, {}, {}, {},
                                     models::TrackingType::kLinearFallback, {},
                                     {}, {});
  const auto& old_etas = tracking_data.GetEtas();
  ASSERT_EQ(old_etas.size(), 2);
  ASSERT_EQ(old_etas[0].tracking_type, models::TrackingType::kLinearFallback);
  ASSERT_EQ(old_etas[1].tracking_type, models::TrackingType::kLinearFallback);
  // ASSERT_EQ(all_point_etas.size(), 4);
  // ASSERT_EQ(all_point_etas[0].tracking_type,
  //           models::TrackingType::kRouteTracking);
  // ASSERT_EQ(all_point_etas[1].tracking_type,
  //           models::TrackingType::kRouteTracking);
  // ASSERT_EQ(all_point_etas[2].tracking_type,
  //           models::TrackingType::kUnknownDestination);
  // ASSERT_EQ(all_point_etas[3].tracking_type,
  //           models::TrackingType::kUnknownDestination);
}

}  // namespace
