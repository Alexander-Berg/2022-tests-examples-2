#include "restore_from_storage.hpp"

#include "internal/unittest_utils/test_utils.hpp"
#include "internal/worker/worker_fsm/event_names.hpp"
#include "internal/worker/worker_fsm/worker_fsm.hpp"
#include "statistics/route_watcher_statistics.hpp"
#include "types/types.hpp"

#include <gtest/gtest.h>

namespace driver_route_watcher {
namespace {
std::optional<models::PersistentTrackingData> MakeDbEntry(
    const models::Position& src, const models::Destination& destination,
    models::TrackingType tracking_type,
    models::TimePoint tracking_since = utils::datetime::Now()) {
  driver_route_watcher::models::PersistentTrackingData ret;
  ret.route = test_utils::MakeTwoPointsRoute(
      {src, destination.ExpressDestinationAsPosition()});
  ret.data = models::TrackingData(
      destination, src,
      {{*ret.route.info.time, *ret.route.info.distance, tracking_type}}, {}, {},
      {src, std::nullopt, std::nullopt, std::nullopt, tracking_since,
       models::TransportType::kCar,
       driver_route_watcher::models::Adjusted::kNo},
      {}, tracking_type, tracking_since, {}, std::nullopt);
  return ret;
}
}  // namespace
}  // namespace driver_route_watcher

TEST(restore_from_storage, base) {
  using driver_route_watcher::MakeDbEntry;
  using driver_route_watcher::internal::fsm::RouteWatcherFsm;
  using driver_route_watcher::models::Destination;
  using driver_route_watcher::models::PersistentTrackingData;
  using driver_route_watcher::models::Position;
  using driver_route_watcher::statistics::RouteWatcherStatistics;
  using driver_route_watcher::test_utils::MakeDestination;
  using namespace driver_route_watcher::internal::events;

  driver_route_watcher::statistics::RouteWatcherStatistics stats;
  const auto src = Position{36 * geometry::lon, 56 * geometry::lat};
  const auto dst = Position{37 * geometry::lon, 56 * geometry::lat};
  auto destination = MakeDestination(dst);
  {
    auto db_entry =
        MakeDbEntry(src, destination,
                    driver_route_watcher::models::TrackingType::kRouteTracking);
    auto state = driver_route_watcher::internal::GetState(
                     db_entry->data.GetTrackingType())
                     ->GetName();
    const auto expected =
        driver_route_watcher::internal::fsm::TrackingState::GetStateInstance()
            ->GetName();
    EXPECT_EQ(expected, state);
  }
  {
    auto db_entry = MakeDbEntry(
        src, destination,
        driver_route_watcher::models::TrackingType::kLinearFallback);
    EXPECT_EQ(db_entry->data.GetTrackingType(),
              driver_route_watcher::models::TrackingType::kLinearFallback);
    auto state = driver_route_watcher::internal::GetState(
                     db_entry->data.GetTrackingType())
                     ->GetName();
    const auto expected = driver_route_watcher::internal::fsm::
                              FallbackTrackingState::GetStateInstance()
                                  ->GetName();
    EXPECT_EQ(expected, state);
  }
  {
    auto db_entry = MakeDbEntry(
        src, destination,
        driver_route_watcher::models::TrackingType::kUnknownDestination);
    auto state = driver_route_watcher::internal::GetState(
                     db_entry->data.GetTrackingType())
                     ->GetName();
    const auto expected = driver_route_watcher::internal::fsm::
                              UnknownDestinationState::GetStateInstance()
                                  ->GetName();
    EXPECT_EQ(expected, state);
  }
}
