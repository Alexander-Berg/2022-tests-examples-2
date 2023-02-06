#include <gtest/gtest.h>

#include "internal/unittest_utils/test_utils.hpp"
#include "worker.hpp"

#include <userver/utest/utest.hpp>

namespace {
const auto kTransportType = driver_route_watcher::models::TransportType::kCar;
const auto kAdjusted = driver_route_watcher::models::Adjusted::kNo;
namespace drwi = driver_route_watcher::internal;
namespace drwm = driver_route_watcher::models;
using driver_route_watcher::test_utils::MakeDestination;

using drwi::fsm::RouteRebuildState;
using drwi::fsm::RouteRequestState;
using drwi::fsm::TrackingState;
using drwi::fsm::UnknownDestinationState;
using drwi::fsm::WaitDataState;
using ::geometry::lat;
using ::geometry::lon;

::geobus::types::Message<geobus::types::DriverPosition> MakePositionMessage(
    const drwm::DriverId& driver_id, const ::geometry::Position& position) {
  ::geobus::types::Message<geobus::types::DriverPosition> ret;
  geobus::types::DriverPosition pos;
  driver_id::DriverDbidUndscrUuid dbid_uuid(driver_id.GetDriverId().GetDbid(),
                                            driver_id.GetDriverId().GetUuid());
  pos.driver_id = dbid_uuid;
  pos.signal = ::gpssignal::GpsSignal(position.latitude, position.longitude);
  ret.data.push_back(pos);
  return ret;
}

drwm::FsmRestoreData MakeStoredData(const ::geometry::Position& position,
                                    const drwm::Destination& destination,
                                    drwm::FsmStateType current_state) {
  using driver_route_watcher::test_utils::MakeTwoPointsRoute;

  drwm::FsmRestoreData restore_data;
  restore_data.route = MakeTwoPointsRoute(
      {position, destination.ExpressDestinationAsPosition()});
  restore_data.driver_position = drwm::DriverPosition(
      position, std::nullopt, std::nullopt, std::nullopt, {}, {}, {});
  restore_data.current_state = current_state;

  return restore_data;
}

}  // namespace

UTEST(worker, test_slave_skip_messages) {
  const auto driver_id = drwm::DriverId(driver_id::DriverDbid("dbid"),
                                        driver_id::DriverUuid("uuid"));
  driver_route_watcher::test_utils::Env env;
  {
    auto config_ptr = env.config_->StartWrite();
    config_ptr->SetEnableAllPointRouting(true);
    config_ptr.Commit();
  }

  auto deps = env.deps;
  auto worker = driver_route_watcher::internal::Worker(deps);

  // Send message
  worker.StartWatch(driver_id, {});
  // Process message
  worker.ProcessMessages();
  // Skip
  /// TODO(dolovnyak) it commented while both fsm works
  // ASSERT_EQ(1, deps->GetStats().GetWorkerMessagesSkipBySlaves());

  // Send message
  ::geometry::Position position(37 * geometry::lon, 55 * geometry::lat);
  worker.SetPositions(MakePositionMessage(driver_id, position), kTransportType,
                      kAdjusted);
  // Process message
  worker.ProcessMessages();
  // Skip
  /// TODO(dolovnyak): commented while both fsm works
  // ASSERT_EQ(2, deps->GetStats().GetWorkerMessagesSkipBySlaves());
}

UTEST(worker, test_master_happy_path) {
  using drwm::ServiceId;

  const auto service_id = ServiceId("some-service_id");
  const auto driver_id = drwm::DriverId(driver_id::DriverDbid("dbid"),
                                        driver_id::DriverUuid("uuid"));
  ::geometry::Position source(37 * geometry::lon, 55 * geometry::lat);
  ::geometry::Position position(37 * geometry::lon, 55.5 * geometry::lat);
  auto destination =
      MakeDestination({37 * geometry::lon, 56 * geometry::lat}, service_id);

  driver_route_watcher::test_utils::Env env;
  {
    auto config_ptr = env.config_->StartWrite();
    config_ptr->SetEnableAllPointRouting(true);
    config_ptr.Commit();
  }
  auto deps = env.deps;
  auto& stats = deps->GetStats();
  auto& storage = env.storage_;
  auto worker = driver_route_watcher::internal::Worker(deps);
  // Store to db initial state
  storage.SetWatch(driver_id, destination);

  // Restore from db by WatchesSynchronizer (after fullscan)
  worker.SetDestinations(driver_id, {{service_id, destination}});
  worker.ProcessMessages();

  // Become master
  env.master_slave_.SetIsMaster(1);

  // Send position
  worker.SetPositions(MakePositionMessage(driver_id, source), kTransportType,
                      kAdjusted);
  worker.ProcessMessages();
  //   Do not skip (master)
  ASSERT_EQ(0, stats.GetWorkerMessagesSkipBySlaves());
  //   No record in db (not watched yet)
  ASSERT_FALSE(storage.GetFsmRestoreData(driver_id));

  // Set destination
  worker.StartWatch(driver_id, destination);
  worker.ProcessMessages();
  //   Do not skip (master)
  ASSERT_EQ(0, stats.GetWorkerMessagesSkipBySlaves());
  //   No record in db (not watched yet)
  ASSERT_FALSE(storage.GetFsmRestoreData(driver_id));

  // Wait route (should be requested as we have current position and
  // destination. result must be placed in message queue)
  worker.ProcessMessages();
  //   Do not skip (master)
  ASSERT_EQ(0, stats.GetWorkerMessagesSkipBySlaves());
  //   Has record in db (has source, destination and route)
  auto record0 = storage.GetFsmRestoreData(driver_id);
  ASSERT_TRUE(record0);
  ASSERT_EQ(2ul, record0->route->path.size());
  ASSERT_EQ(drwm::FsmStateType::kTracking, record0->current_state);

  // Update current position
  worker.SetPositions(MakePositionMessage(driver_id, position), kTransportType,
                      kAdjusted);
  worker.ProcessMessages();
  //   Do not skip (master)
  ASSERT_EQ(0, stats.GetWorkerMessagesSkipBySlaves());

  // Stop watch
  worker.StopWatch(driver_id, destination);
  worker.ProcessMessages();
  //   Do not skip (master)
  ASSERT_EQ(0, stats.GetWorkerMessagesSkipBySlaves());
  //   No record in db (not watched now)
  ASSERT_FALSE(storage.GetFsmRestoreData(driver_id));
  ASSERT_TRUE(storage.output.empty());
  ASSERT_TRUE(storage.routes.empty());

  /// TODO(dolovnyak) commented while both fsm work
  // EXPECT_EQ(0ul, stats.GetRebuildOldRoute());
  // EXPECT_EQ(1ul, stats.GetRestoreTries());
  // EXPECT_EQ(0ul, stats.GetRestoredToTracking());
  // EXPECT_EQ(0ul, stats.GetAdjustFailed());
  // EXPECT_EQ(1ul, stats.GetAdjustOk());
  // EXPECT_EQ(1ul, stats.GetRoutesRequested());  // Has requested route
  // EXPECT_EQ(2ul, storage.outputs_updated);
}

/// Test simple restoring from db
///   1. no local info about driver
///   2. immediately after becoming master recive Destinations from
///      WatchesSynchronizer. On receive Destinations try to get output from db
///      TODO: get output with watches on scan (no need to do it separately)
///   4. normal processing (should try to adjust(success) )
///   5. no route request must be performed in this case
UTEST(worker, test_restore_happy_path) {
  using driver_route_watcher::models::DestinationsByService;
  using driver_route_watcher::models::ServiceId;

  const auto service0 = ServiceId("service0");
  const auto service1 = ServiceId("service1");
  const auto driver_id = drwm::DriverId(driver_id::DriverDbid("dbid"),
                                        driver_id::DriverUuid("uuid"));
  const auto source =
      ::geometry::Position(37 * geometry::lon, 55 * geometry::lat);
  const auto destination0 =
      MakeDestination({37 * geometry::lon, 56 * geometry::lat}, service0);
  const auto destination1 =
      MakeDestination({38 * geometry::lon, 57 * geometry::lat}, service1);
  const auto destinations = DestinationsByService{
      {service0, destination0},
      {service1, destination1},
  };
  ::geometry::Position position(37 * geometry::lon, 55.5 * geometry::lat);

  driver_route_watcher::test_utils::Env env;
  {
    auto config_ptr = env.config_->StartWrite();
    config_ptr->SetServicePriorityConfig({{"service0", 100}});
    config_ptr->SetEnableAllPointRouting(true);
    config_ptr.Commit();
  }

  // Prepare storage
  auto& storage = env.storage_;
  auto tracking_data = drwm::TrackingData::MakeAllPointsRoutingTrackingData(
      {}, {}, {}, {}, {}, {}, {}, {}, {}, {});
  auto data0 =
      MakeStoredData(source, destination0, drwm::FsmStateType::kTracking);
  auto data1 = MakeStoredData(source, destination1,
                              drwm::FsmStateType::kFallbackTracking);

  storage.SetFsmRestoreData(driver_id, tracking_data, data0.route,
                            data0.driver_position, data0.current_state, {});

  // Initial update count
  ASSERT_EQ(1ul, storage.outputs_updated);

  // Become master
  env.master_slave_.SetIsMaster(1);
  auto deps = env.deps;
  auto& stats = deps->GetStats();
  auto worker = drwi::Worker(deps);
  const auto worker_viewer =
      driver_route_watcher::test_utils::TestWorkerViewer(worker);

  // Set destinations (in real app destiantions sent by WatchesSynchronizer
  // after full scan of watched destinations)
  worker.SetDestinations(driver_id, destinations);
  worker.ProcessMessages();

  // Send position
  worker.SetPositions(MakePositionMessage(driver_id, position), kTransportType,
                      kAdjusted);
  worker.ProcessMessages();
  //   Do not skip (master)
  EXPECT_EQ(0, stats.GetWorkerMessagesSkipBySlaves());
  /// TODO(dolovnyak): commented while both fsm works
  // EXPECT_EQ(1ul, stats.GetRestoreTries());
  // EXPECT_EQ(1ul, stats.GetRestoredToTracking());
  // EXPECT_EQ(0ul, stats.GetAdjustFailed());
  // EXPECT_EQ(1ul, stats.GetAdjustOk());
  // EXPECT_EQ(0ul, stats.GetRoutesRequested());
  // EXPECT_EQ(2ul, storage.outputs_updated);
  auto& local = worker_viewer.GetLocalStorage();
  const auto& watcher = local.GetByDriverId(driver_id);
  const auto& watcher_data = watcher.GetData();
  const auto& destinations_by_service = watcher_data.GetDestinationsByService();
  ASSERT_EQ(2ul, destinations_by_service.size());
}

UTEST(worker, test_restore_from_route_request) {
  const auto driver_id = drwm::DriverId(driver_id::DriverDbid("dbid"),
                                        driver_id::DriverUuid("uuid"));
  ::geometry::Position source(37 * geometry::lon, 55 * geometry::lat);
  auto destination = MakeDestination({37 * geometry::lon, 56 * geometry::lat});

  driver_route_watcher::test_utils::Env env;
  {
    auto config_ptr = env.config_->StartWrite();
    config_ptr->SetEnableAllPointRouting(true);
    config_ptr.Commit();
  }
  // Become master
  env.master_slave_.SetIsMaster(1);
  auto deps = env.deps;
  auto& stats = deps->GetStats();
  auto& storage = env.storage_;
  auto worker = drwi::Worker(deps);

  // Send position
  worker.SetPositions(MakePositionMessage(driver_id, source), kTransportType,
                      kAdjusted);
  worker.ProcessMessages();

  // Set destination
  worker.StartWatch(driver_id, destination);
  worker.ProcessMessages();

  // Clear message queue to leave watch in RouteRequestState
  //
  worker.ClearInputMessagesQueue(std::chrono::milliseconds(500), 1);

  // Prepare storage
  auto tracking_data = drwm::TrackingData::MakeAllPointsRoutingTrackingData(
      {}, {}, {}, {}, {}, {}, {}, {}, {}, {});
  auto data = MakeStoredData(source, destination,
                             drwm::FsmStateType::kUnknownDestination);
  storage.SetFsmRestoreData(driver_id, tracking_data, data.route,
                            data.driver_position, data.current_state, {});

  // Increase Master count to force restore from db
  env.master_slave_.SetIsMaster(2);

  worker.StopWatch(driver_id, destination);
  worker.ProcessMessages();

  //   Do not skip (master)
  ASSERT_EQ(0, stats.GetWorkerMessagesSkipBySlaves());
  //   No record in db (not watched now)
  ASSERT_FALSE(storage.GetFsmRestoreData(driver_id));
  ASSERT_TRUE(storage.restore_data.empty());
  ASSERT_TRUE(storage.routes.empty());
}

UTEST(worker, test_remove_output_in_route_request_on_stop_watch) {
  const auto driver_id = drwm::DriverId(driver_id::DriverDbid("dbid"),
                                        driver_id::DriverUuid("uuid"));
  ::geometry::Position source(37 * geometry::lon, 55 * geometry::lat);
  auto destination = MakeDestination({37 * geometry::lon, 56 * geometry::lat});
  ::geometry::Position position_out_of_path(37.5 * geometry::lon,
                                            55.5 * geometry::lat);

  driver_route_watcher::test_utils::Env env;
  {
    auto config_ptr = env.config_->StartWrite();
    config_ptr->SetEnableAllPointRouting(true);
    config_ptr.Commit();
  }
  // Become master
  env.master_slave_.SetIsMaster(1);
  auto deps = env.deps;
  auto& stats = deps->GetStats();
  auto& storage = env.storage_;
  auto worker = driver_route_watcher::internal::Worker(deps);

  // Set watch in tracking state
  //   Send position
  worker.SetPositions(MakePositionMessage(driver_id, source), kTransportType,
                      kAdjusted);
  worker.ProcessMessages();

  //   Set destination
  worker.StartWatch(driver_id, destination);
  worker.ProcessMessages();

  //   Process route message, switch to tracking state
  worker.ProcessMessages();
  ASSERT_TRUE(storage.GetFsmRestoreData(driver_id));  // Check we in tracking

  // Set current position out of route
  ASSERT_EQ(0ul, stats.GetAdjustFailed());
  ASSERT_EQ(0ul, stats.GetAdjustOk());

  worker.SetPositions(MakePositionMessage(driver_id, position_out_of_path),
                      kTransportType, kAdjusted);
  worker.ProcessMessages();  // Process position message

  /// TODO(dolovnyak): commented while both fsm works
  // ASSERT_EQ(1ul, stats.GetAdjustFailed());
  // ASSERT_EQ(0ul, stats.GetAdjustOk());

  // Clear message queue to leave watch in RouteRequestState
  worker.ClearInputMessagesQueue(std::chrono::milliseconds(500), 1);

  worker.StopWatch(driver_id, destination);
  worker.ProcessMessages();

  // Do not skip (master)
  ASSERT_EQ(0, stats.GetWorkerMessagesSkipBySlaves());
  // No record in db (not watched now)
  ASSERT_FALSE(storage.GetFsmRestoreData(driver_id));
  ASSERT_TRUE(storage.output.empty());
  ASSERT_TRUE(storage.routes.empty());
}

/// Test that drivers that has destinations but do not has position counted as
/// watched
UTEST(worker, test_count_watched_without_positions) {
  const auto driver_id = drwm::DriverId(driver_id::DriverDbid("dbid"),
                                        driver_id::DriverUuid("uuid"));
  auto destination = MakeDestination({37 * geometry::lon, 56 * geometry::lat});

  driver_route_watcher::test_utils::Env env;
  {
    auto config_ptr = env.config_->StartWrite();
    config_ptr->SetEnableAllPointRouting(true);
    config_ptr.Commit();
  }
  // Become master
  env.master_slave_.SetIsMaster(1);
  auto deps = env.deps;
  auto worker = driver_route_watcher::internal::Worker(deps);

  std::unordered_map<drwm::DriverId, drwm::Destination> watched;
  driver_route_watcher::statistics::StateStats state_stats;

  // Set destination (but position is nullopt)
  worker.StartWatch(driver_id, destination);
  worker.ProcessMessages();

  worker.GetWatched(watched);
  ASSERT_EQ(0ul, watched.size());

  // Add position in cache
  env.positions_cache_.emplace(
      driver_id,
      drwm::DriverPosition(10 * lat, 10 * lon, kTransportType, kAdjusted));
  worker.StartWatch(driver_id, destination);
  worker.ProcessMessages();

  worker.GetWatched(watched);
  ASSERT_NO_THROW(watched.at(driver_id));
  ASSERT_EQ(1ul, watched.size());

  worker.GetStats(state_stats);
  ASSERT_EQ(1ul, state_stats.watched.Load());
  ASSERT_EQ(0ul, state_stats.tracking.Load());
  ASSERT_EQ(0ul, state_stats.fallback.Load());
  ASSERT_EQ(1ul, state_stats.waiting_position.Load());
}

/// Case when we got route but failed to adjust new position that we got when
/// waited for route.
/// We must get result of route rerequest after failed to adjust in
/// RouteRequestState
UTEST(worker, test_request_not_canceled) {
  const auto driver_id = drwm::DriverId(driver_id::DriverDbid("dbid"),
                                        driver_id::DriverUuid("uuid"));
  ::geometry::Position source(37 * geometry::lon, 55 * geometry::lat);
  auto destination = MakeDestination({37 * geometry::lon, 56 * geometry::lat});
  ::geometry::Position position_out_of_path(37.5 * geometry::lon,
                                            55.5 * geometry::lat);

  driver_route_watcher::test_utils::Env env;
  {
    auto config_ptr = env.config_->StartWrite();
    config_ptr->SetEnableAllPointRouting(true);
    config_ptr.Commit();
  }
  // Become master
  env.master_slave_.SetIsMaster(1);
  auto deps = env.deps;
  auto worker = driver_route_watcher::internal::Worker(deps);
  auto worker_viewer =
      driver_route_watcher::test_utils::TestWorkerViewer(worker);

  // Set watch in tracking state
  //   Send position
  worker.SetPositions(MakePositionMessage(driver_id, source), kTransportType,
                      kAdjusted);
  worker.ProcessMessages();

  //   Set destination
  worker.StartWatch(driver_id, destination);
  worker.ProcessMessages();  /// process startWatch, request route

  {
    auto& data = worker_viewer.GetLocalStorage().GetByDriverId(driver_id);
    const auto& fsm = data.GetFsm();
    ASSERT_EQ(fsm.GetCurrentState()->GetName(),
              fsm.GetStateInstance<RouteRequestState>()->GetName());
  }

  /// set out of path position
  worker.SetPositions(MakePositionMessage(driver_id, position_out_of_path),
                      kTransportType, kAdjusted);
  {
    auto& data = worker_viewer.GetLocalStorage().GetByDriverId(driver_id);
    const auto& fsm = data.GetFsm();
    ASSERT_EQ(fsm.GetCurrentState()->GetName(),
              fsm.GetStateInstance<RouteRequestState>()->GetName());
  }
  worker.ProcessMessages();  // Process route ok message
  worker.ProcessMessages();  // Process positions message with invalid pos
  worker.ProcessMessages();  // Process route ok message
  {
    auto& data = worker_viewer.GetLocalStorage().GetByDriverId(driver_id);
    const auto& fsm = data.GetFsm();
    ASSERT_EQ(fsm.GetCurrentState()->GetName(),
              fsm.GetStateInstance<TrackingState>()->GetName());
  }
}

// Add More tests with master/slave state changes
