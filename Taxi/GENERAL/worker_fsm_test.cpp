#include <gtest/gtest.h>

#include <userver/utest/utest.hpp>
#include <userver/utils/mock_now.hpp>

#include "statistics/route_watcher_statistics.hpp"

#include "internal/position_helper.hpp"
#include "internal/unittest_utils/test_utils.hpp"
#include "internal/worker/worker_dependencies.hpp"
#include "worker_fsm.hpp"
#include "worker_fsm_data.hpp"

namespace {
const auto kTransportType = driver_route_watcher::models::TransportType::kCar;
const auto kAdjusted = driver_route_watcher::models::Adjusted::kNo;

namespace drw = driver_route_watcher;
namespace drwi = driver_route_watcher::internal;
namespace drwm = driver_route_watcher::models;
using drw::test_utils::MakeDestination;
using drw::test_utils::MakeUnknownDestination;
using drwi::fsm::FallbackTrackingState;
using drwi::fsm::RouteRebuildState;
using drwi::fsm::RouteRequestState;
using drwi::fsm::TrackingState;
using drwi::fsm::UnknownDestinationState;
using drwi::fsm::WaitDataState;
using ::geometry::lat;
using ::geometry::lon;
using BlockingPopTimeout = drwi::InputMessagesQueue::BlockingPopTimeout;
}  // namespace

struct TwoCombinedServicesData {
  const drwm::ServiceId service_id = drwm::ServiceId("processing:transporting");
  const drwm::ServiceId chained_service_id =
      drwm::ServiceId("processing:driving");
  const drwm::DriverPosition src_pos = drwm::DriverPosition(
      10 * geometry::lat, 10 * geometry::lon,
      driver_route_watcher::models::TransportType::kCar, kAdjusted);
  const drwm::Destination dst =
      driver_route_watcher::test_utils::MakeDestination(
          {10 * geometry::lat, 20 * geometry::lon}, service_id,
          utils::datetime::Now() - std::chrono::seconds(20));
  const drwm::Destination chained_dst =
      driver_route_watcher::test_utils::MakeDestination(
          drwm::DriverPosition(
              10 * geometry::lat, 11 * geometry::lon,
              driver_route_watcher::models::TransportType::kCar, kAdjusted),
          chained_service_id);
  const drwm::DriverPosition not_adjustible = drwm::DriverPosition(
      11 * geometry::lat, 11 * geometry::lon,
      driver_route_watcher::models::TransportType::kCar, kAdjusted);

  const drwm::DriverId driver_id = drwm::DriverId(
      driver_id::DriverDbid("dbid"), driver_id::DriverUuid("uuid"));
};

void ProcessRoute(drwi::fsm::RouteWatcherFsm& fsm,
                  drw::test_utils::WorkerFsmEnvironment& env) {
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<drwi::fsm::RouteRequestState>()->GetName());
  // Wait route response appear in message queue
  auto deadline = engine::Deadline::FromDuration(std::chrono::seconds(3));
  drwi::InputMessage message = env.message_queue.BlockingPop(deadline);
  const auto& route_message = std::get<drwi::RouteMessage>(message.data);

  // Received route succesfully, pass it to fsm, should switch to Tracking
  fsm.SetRoute(*env.context, std::move(*route_message.route),
               route_message.request_id,
               std::move(route_message.request_reason),
               route_message.first_segment_was_rebuilt);
}

void ProcessRouteFail(drwi::fsm::RouteWatcherFsm& fsm,
                      drw::test_utils::WorkerFsmEnvironment& env) {
  // Wait route response appear in message queue
  auto deadline = engine::Deadline::FromDuration(std::chrono::seconds(3));
  drwi::InputMessage message = env.message_queue.BlockingPop(deadline);
  const auto& route_message = std::get<drwi::RouteFailedMessage>(message.data);

  fsm.SetRouteFailed(*env.context, route_message.request_id,
                     route_message.reason,
                     std::move(route_message.request_reason));
}

void SetToSimpleTrackingState(drwi::fsm::RouteWatcherFsm& fsm,
                              drw::test_utils::WorkerFsmEnvironment& env,
                              const TwoCombinedServicesData& test_data) {
  const auto& src_pos = test_data.src_pos;
  const auto& dst = test_data.dst;

  drwi::Config new_config;
  new_config.SetServicePriorityConfig({
      {"processing:transporting", 100},
      {"processing:driving", 90},
  });
  new_config.SetEnableAllPointRouting(true);
  env.SetConfig(new_config);

  // Set position (gps)
  // Set destination (start-watch)
  fsm.SetPosition(*env.context, src_pos);
  fsm.SetDestination(*env.context, dst);
  ProcessRoute(fsm, env);
}

UTEST(worker_fsm, happy_path) {
  drwm::DriverPosition src_pos(10 * lat, 10 * lon, kTransportType, kAdjusted);
  auto dst_pos = MakeDestination({10 * lat, 20 * lon});
  drwm::DriverPosition pos1(10 * lat, 11 * lon, kTransportType,
                            kAdjusted);  // Move along the route
  auto invalid_dst = MakeDestination(pos1);

  drwm::DriverPosition pos2(10 * lat, 12 * lon, kTransportType, kAdjusted);
  const auto driver_id = drwm::DriverId(driver_id::DriverDbid("dbid"),
                                        driver_id::DriverUuid("uuid"));

  drw::test_utils::WorkerFsmEnvironment env(driver_id);
  drwi::Config config;
  config.SetEnableAllPointRouting(true);
  env.SetConfig(config);

  // Initial state
  drwi::fsm::RouteWatcherFsm fsm;
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<WaitDataState>()->GetName());

  // Set position (gps)
  fsm.SetPosition(*env.context, src_pos);
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<WaitDataState>()->GetName());

  // Set destination (start-watch)
  // route request should be triggered
  fsm.SetDestination(*env.context, dst_pos);
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<RouteRequestState>()->GetName());

  {
    // Now watched
    auto output_ptr = env.output[driver_id]->Lock();
    ASSERT_FALSE(output_ptr->IsDeleted());
  }
  ASSERT_FALSE(env.storage_.GetFsmRestoreData(driver_id));

  // Wait route response appear in message queue
  auto deadline = engine::Deadline::FromDuration(std::chrono::seconds(3));
  drwi::InputMessage message = env.message_queue.BlockingPop(deadline);
  const auto& route_message = std::get<drwi::RouteMessage>(message.data);
  ASSERT_EQ(route_message.driver_id.GetDriverId().dbid,
            driver_id::DriverDbid("dbid"));
  ASSERT_EQ(route_message.driver_id.GetDriverId().uuid,
            driver_id::DriverUuid("uuid"));
  ASSERT_EQ(route_message.request_id, env.data.GetRouteRequestId());
  ASSERT_NE(route_message.route, nullptr);
  ASSERT_EQ(0ul, env.storage_.outputs_updated);

  // Received route succesfully, pass it to fsm, should switch to Tracking
  fsm.SetRoute(*env.context, std::move(*route_message.route),
               route_message.request_id,
               std::move(route_message.request_reason),
               route_message.first_segment_was_rebuilt);
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<TrackingState>()->GetName());
  ASSERT_EQ(1ul, env.storage_.outputs_updated);

  {
    // Has TrackingState output now
    // TODO: Values are dummy, should be changed after AdjusterIntegration
    auto output_ptr = env.output[driver_id]->Lock();
    ASSERT_FALSE(output_ptr->IsDeleted());
    const auto& output_destination = output_ptr->GetDestination();
    ASSERT_TRUE(drwi::IsEqual(output_destination.ExpressDestinationAsPosition(),
                              dst_pos.ExpressDestinationAsPosition()));
    ASSERT_EQ(output_destination.service_id.GetUnderlying(), "some-service-id");
    ASSERT_EQ(output_destination.metainfo, "some-meta-info");
  }
  {
    auto output = env.storage_.GetFsmRestoreData(driver_id);
    ASSERT_TRUE(output);
    ASSERT_TRUE(output->current_state == drwm::FsmStateType::kTracking);
  }

  // Receive some positions in tracking state
  for (const auto& pos : {pos1, pos2}) {
    fsm.SetPosition(*env.context, pos);
    ASSERT_EQ(fsm.GetCurrentState()->GetName(),
              fsm.GetStateInstance<TrackingState>()->GetName());
  }
  ASSERT_EQ(3ul, env.storage_.outputs_updated);

  {
    // Has TrackingState output now
    // !!! Values are dummy, should be changed after AdjusterIntegration
    auto output_ptr = env.output[driver_id]->Lock();
    ASSERT_FALSE(output_ptr->IsDeleted());
    ASSERT_TRUE(drwi::IsEqual(
        output_ptr->GetDestination().ExpressDestinationAsPosition(),
        dst_pos.ExpressDestinationAsPosition()));
  }
  {
    auto output = env.storage_.GetFsmRestoreData(driver_id);
    ASSERT_TRUE(output);
    ASSERT_TRUE(output->current_state == drwm::FsmStateType::kTracking);
  }

  // Try reset destination with invalid position (not actualy watching)
  fsm.ResetDestination(*env.context, invalid_dst);
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<TrackingState>()->GetName());
  ASSERT_EQ(3ul, env.storage_.outputs_updated);

  // Reset destination (pass correct destination)
  fsm.ResetDestination(*env.context, dst_pos);
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<WaitDataState>()->GetName());
  ASSERT_EQ(1ul, env.storage_.outputs_cleared);
}

UTEST(worker_fsm, fallback) {
  drwm::DriverPosition src_pos(10 * lat, 10 * lon, kTransportType, kAdjusted);
  drwm::DriverPosition pos1(10 * lat, 11 * lon, kTransportType,
                            kAdjusted);  // Move along the route
  auto dst_pos = MakeDestination({10 * lat, 20 * lon});
  auto invalid_dst = MakeDestination(pos1);

  // turn from route by 90 deg.
  drwm::DriverPosition pos2(11 * lat, 11 * lon, kTransportType, kAdjusted);
  const auto driver_id = drwm::DriverId(driver_id::DriverDbid("dbid"),
                                        driver_id::DriverUuid("uuid"));
  drw::test_utils::WorkerFsmEnvironment env(driver_id);

  driver_route_watcher::internal::Config config;
  config.SetEnableAllPointRouting(true);
  env.SetConfig(config);

  // Break main router
  env.router.SetThrow();

  // Initial state
  drwi::fsm::RouteWatcherFsm fsm;
  fsm.SetPosition(*env.context, src_pos);
  fsm.SetDestination(*env.context, dst_pos);

  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<RouteRequestState>()->GetName());

  // Wait route response appear in message queue
  auto deadline = engine::Deadline::FromDuration(std::chrono::seconds(3));
  drwi::InputMessage message = env.message_queue.BlockingPop(deadline);
  const auto& route_message = std::get<drwi::RouteFailedMessage>(message.data);
  ASSERT_EQ(route_message.driver_id.GetDriverId().dbid,
            driver_id::DriverDbid("dbid"));
  ASSERT_EQ(route_message.driver_id.GetDriverId().uuid,
            driver_id::DriverUuid("uuid"));
  ASSERT_EQ(route_message.request_id, env.data.GetRouteRequestId());

  // Received route failed, pass it to fsm, should switch to FalbackTracking
  fsm.SetRouteFailed(*env.context, route_message.request_id,
                     route_message.reason,
                     std::move(route_message.request_reason));
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<FallbackTrackingState>()->GetName());

  {
    // Has TrackingState output now
    // Values are dummy, should be changed after AdjusterIntegration
    auto output_ptr = env.output[driver_id]->Lock();
    ASSERT_FALSE(output_ptr->IsDeleted());
    const auto& output_destination = output_ptr->GetDestination();
    ASSERT_TRUE(drwi::IsEqual(output_destination.ExpressDestinationAsPosition(),
                              dst_pos.ExpressDestinationAsPosition()));
    ASSERT_EQ(output_destination.service_id.GetUnderlying(), "some-service-id");
    ASSERT_EQ(output_destination.metainfo, "some-meta-info");
  }
  {
    auto output = env.storage_.GetFsmRestoreData(driver_id);
    ASSERT_TRUE(output);
    ASSERT_TRUE(output->current_state == drwm::FsmStateType::kFallbackTracking);
  }

  // Receive some positions in tracking state
  for (const auto& pos : {pos1, pos2}) {
    fsm.SetPosition(*env.context, pos);
    ASSERT_EQ(fsm.GetCurrentState()->GetName(),
              fsm.GetStateInstance<FallbackTrackingState>()->GetName());
  }

  {
    // Has TrackingState output now
    // Values are dummy, should be changed after AdjusterIntegration
    auto output_ptr = env.output[driver_id]->Lock();
    ASSERT_FALSE(output_ptr->IsDeleted());
    const auto& output_destination = output_ptr->GetDestination();
    ASSERT_TRUE(drwi::IsEqual(output_destination.ExpressDestinationAsPosition(),
                              dst_pos.ExpressDestinationAsPosition()));
    ASSERT_EQ(output_destination.service_id.GetUnderlying(), "some-service-id");
    ASSERT_EQ(output_destination.metainfo, "some-meta-info");
  }
  {
    auto output = env.storage_.GetFsmRestoreData(driver_id);
    ASSERT_TRUE(output);
    ASSERT_TRUE(output->current_state == drwm::FsmStateType::kFallbackTracking);
  }

  // Try reset destination with invalid position (not actualy watching)
  fsm.ResetDestination(*env.context, invalid_dst);
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<FallbackTrackingState>()->GetName());

  // Reset destination (pass correct destination)
  fsm.ResetDestination(*env.context, dst_pos);
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<WaitDataState>()->GetName());
}

// Test failed to adjust while tracking
UTEST(worker_fsm, failed_to_adjust_while_tracking) {
  drwm::DriverPosition src_pos(10 * lat, 10 * lon, kTransportType, kAdjusted);
  drwm::DriverPosition pos1(10 * lat, 11 * lon, kTransportType,
                            kAdjusted);  // Move along the route
  auto dst_pos = MakeDestination({10 * lat, 20 * lon});
  // turn from route by 90 deg.
  drwm::DriverPosition not_adjustible(11 * lat, 11 * lon, kTransportType,
                                      kAdjusted);
  const auto driver_id = drwm::DriverId(driver_id::DriverDbid("dbid"),
                                        driver_id::DriverUuid("uuid"));
  drw::test_utils::WorkerFsmEnvironment env(driver_id);

  driver_route_watcher::internal::Config config;
  config.SetEnableAllPointRouting(true);
  env.SetConfig(config);

  // Initial state
  drwi::fsm::RouteWatcherFsm fsm;
  fsm.SetPosition(*env.context, src_pos);
  fsm.SetDestination(*env.context, dst_pos);

  // Wait route response appear in message queue
  auto deadline = engine::Deadline::FromDuration(std::chrono::seconds(3));
  drwi::InputMessage message = env.message_queue.BlockingPop(deadline);
  const auto& route_message = std::get<drwi::RouteMessage>(message.data);
  const auto first_request_id = env.data.GetRouteRequestId();
  ASSERT_EQ(route_message.request_id, first_request_id);
  ASSERT_NE(route_message.route, nullptr);

  // Received route succesfully, pass it to fsm, should switch to Tracking
  fsm.SetRoute(*env.context, std::move(*route_message.route),
               route_message.request_id,
               std::move(route_message.request_reason),
               route_message.first_segment_was_rebuilt);
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<TrackingState>()->GetName());

  // Receive some positions in tracking state
  fsm.SetPosition(*env.context, pos1);
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<TrackingState>()->GetName());

  // Should not NOT be adjusted
  // must try rebuild route. Enter to RouteRequestState
  fsm.SetPosition(*env.context, not_adjustible);
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<RouteRequestState>()->GetName());
  {
    // TrackingState output must be still available after last succesfully
    // adjusted position
    auto output_ptr = env.output[driver_id]->Lock();
    ASSERT_FALSE(output_ptr->IsDeleted());
    const auto& output_destination = output_ptr->GetDestination();
    ASSERT_TRUE(drwi::IsEqual(output_destination.ExpressDestinationAsPosition(),
                              dst_pos.ExpressDestinationAsPosition()));
    ASSERT_EQ(output_destination.service_id.GetUnderlying(), "some-service-id");
    ASSERT_EQ(output_destination.metainfo, "some-meta-info");
  }

  {
    auto output = env.storage_.GetFsmRestoreData(driver_id);
    ASSERT_TRUE(output);
    ASSERT_TRUE(output->current_state == drwm::FsmStateType::kTracking);
  }

  // Wait route rebuild response
  {
    drwi::InputMessage message = env.message_queue.BlockingPop(deadline);
    const auto& route_message = std::get<drwi::RouteMessage>(message.data);
    ASSERT_EQ(route_message.driver_id.GetDriverId().dbid,
              driver_id::DriverDbid("dbid"));
    ASSERT_EQ(route_message.driver_id.GetDriverId().uuid,
              driver_id::DriverUuid("uuid"));
    const auto rebuild_request_id = env.data.GetRouteRequestId();
    ASSERT_EQ(route_message.request_id, rebuild_request_id);
    ASSERT_NE(route_message.route, nullptr);

    ASSERT_NE(rebuild_request_id, first_request_id);

    fsm.SetRoute(*env.context, std::move(*route_message.route),
                 route_message.request_id,
                 std::move(route_message.request_reason),
                 route_message.first_segment_was_rebuilt);
    /// Should return to tracking state
    ASSERT_EQ(fsm.GetCurrentState()->GetName(),
              fsm.GetStateInstance<TrackingState>()->GetName());
  }

  {
    // Has TrackingState output now
    // Values are dummy, should be changed after AdjusterIntegration
    auto output_ptr = env.output[driver_id]->Lock();
    ASSERT_FALSE(output_ptr->IsDeleted());
    const auto& output_destination = output_ptr->GetDestination();
    ASSERT_TRUE(drwi::IsEqual(output_destination.ExpressDestinationAsPosition(),
                              dst_pos.ExpressDestinationAsPosition()));
    ASSERT_EQ(output_destination.service_id.GetUnderlying(), "some-service-id");
    ASSERT_EQ(output_destination.metainfo, "some-meta-info");
  }
  {
    auto output = env.storage_.GetFsmRestoreData(driver_id);
    ASSERT_TRUE(output);
    ASSERT_TRUE(output->current_state == drwm::FsmStateType::kTracking);

    ASSERT_TRUE(
        ::geometry::AreClosePositions(output->driver_position, not_adjustible));
  }
}

// TODO: replace with parametrize (same as fallback test)
// Test flow with broken main router (one point route)
UTEST(worker_fsm, one_point_rotue) {
  drwm::DriverPosition src_pos(10 * lat, 10 * lon, kTransportType, kAdjusted);
  drwm::DriverPosition pos1(10 * lat, 11 * lon, kTransportType,
                            kAdjusted);  // Move along the route
  auto dst_pos = MakeDestination({10 * lat, 20 * lon});
  auto invalid_dst = MakeDestination(pos1);

  // turn from route by 90 deg.
  drwm::DriverPosition pos2(11 * lat, 11 * lon, kTransportType, kAdjusted);
  const auto driver_id = drwm::DriverId(driver_id::DriverDbid("dbid"),
                                        driver_id::DriverUuid("uuid"));
  drw::test_utils::WorkerFsmEnvironment env(driver_id);

  driver_route_watcher::internal::Config config;
  config.SetEnableAllPointRouting(true);
  env.SetConfig(config);

  // Break main router
  env.router.SetOnePoint();

  // Initial state
  drwi::fsm::RouteWatcherFsm fsm;
  fsm.SetPosition(*env.context, src_pos);
  fsm.SetDestination(*env.context, dst_pos);

  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<RouteRequestState>()->GetName());

  // Wait route response appear in message queue
  auto deadline = engine::Deadline::FromDuration(std::chrono::seconds(3));
  drwi::InputMessage message = env.message_queue.BlockingPop(deadline);
  const auto& route_message = std::get<drwi::RouteFailedMessage>(message.data);
  ASSERT_EQ(route_message.driver_id.GetDriverId().dbid,
            driver_id::DriverDbid("dbid"));
  ASSERT_EQ(route_message.driver_id.GetDriverId().uuid,
            driver_id::DriverUuid("uuid"));
  ASSERT_EQ(route_message.request_id, env.data.GetRouteRequestId());

  // Received route failed, pass it to fsm, should switch to FalbackTracking
  fsm.SetRouteFailed(*env.context, route_message.request_id,
                     route_message.reason,
                     std::move(route_message.request_reason));
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<FallbackTrackingState>()->GetName());

  {
    // Has TrackingState output now
    // Values are dummy, should be changed after AdjusterIntegration
    auto output_ptr = env.output[driver_id]->Lock();
    ASSERT_FALSE(output_ptr->IsDeleted());
    ASSERT_TRUE(drwi::IsEqual(
        output_ptr->GetDestination().ExpressDestinationAsPosition(),
        dst_pos.ExpressDestinationAsPosition()));
  }
  {
    auto output = env.storage_.GetFsmRestoreData(driver_id);
    ASSERT_TRUE(output);
    ASSERT_TRUE(output->current_state == drwm::FsmStateType::kFallbackTracking);
  }

  // Receive some positions in tracking state
  for (const auto& pos : {pos1, pos2}) {
    fsm.SetPosition(*env.context, pos);
    ASSERT_EQ(fsm.GetCurrentState()->GetName(),
              fsm.GetStateInstance<FallbackTrackingState>()->GetName());
  }

  {
    // Has TrackingState output now
    // Values are dummy, should be changed after AdjusterIntegration
    auto output_ptr = env.output[driver_id]->Lock();
    ASSERT_FALSE(output_ptr->IsDeleted());
    ASSERT_TRUE(drwi::IsEqual(
        output_ptr->GetDestination().ExpressDestinationAsPosition(),
        dst_pos.ExpressDestinationAsPosition()));
  }
  {
    auto output = env.storage_.GetFsmRestoreData(driver_id);
    ASSERT_TRUE(output);
    ASSERT_TRUE(output->current_state == drwm::FsmStateType::kFallbackTracking);
  }

  // Try reset destination with invalid position (not actualy watching)
  fsm.ResetDestination(*env.context, invalid_dst);
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<FallbackTrackingState>()->GetName());

  // Reset destination (pass correct destination)
  fsm.ResetDestination(*env.context, dst_pos);
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<WaitDataState>()->GetName());
}

UTEST(worker_fsm, return_from_fallback) {
  drwm::DriverPosition src_pos(10 * lat, 10 * lon, kTransportType, kAdjusted);
  drwm::DriverPosition pos1(10 * lat, 11 * lon, kTransportType,
                            kAdjusted);  // Move along the route
  auto dst_pos = MakeDestination({10 * lat, 20 * lon});

  // turn from route by 90 deg.
  drwm::DriverPosition pos2(11 * lat, 11 * lon, kTransportType, kAdjusted);
  const auto driver_id = drwm::DriverId(driver_id::DriverDbid("dbid"),
                                        driver_id::DriverUuid("uuid"));
  drw::test_utils::WorkerFsmEnvironment env(driver_id);

  driver_route_watcher::internal::Config config;
  config.SetEnableAllPointRouting(true);
  env.SetConfig(config);

  // Break main router
  env.router.SetThrow();

  // Initial state
  drwi::fsm::RouteWatcherFsm fsm;
  fsm.SetPosition(*env.context, src_pos);
  fsm.SetDestination(*env.context, dst_pos);
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<RouteRequestState>()->GetName());

  // Wait route response appear in message queue
  auto deadline = engine::Deadline::FromDuration(std::chrono::seconds(3));
  drwi::InputMessage message = env.message_queue.BlockingPop(deadline);
  const auto& route_message = std::get<drwi::RouteFailedMessage>(message.data);

  const auto now = utils::datetime::Now();
  utils::datetime::MockNowSet(now);
  // Received route failed, pass it to fsm, should switch to FalbackTracking
  fsm.SetRouteFailed(*env.context, route_message.request_id,
                     route_message.reason,
                     std::move(route_message.request_reason));
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<FallbackTrackingState>()->GetName());
  ASSERT_EQ(env.data.GetCurrentStateStartTime(), now);

  auto& stats = env.context->GetStats();
  const auto initial_router_calls = stats.GetRoutesRequested();

  for (auto enabled_return : {true, false}) {
    /// In both cases do not work becaouse of timeout
    config.SetEnableReturnFromFallback(enabled_return);
    config.SetEnableAllPointRouting(true);
    env.SetConfig(config);
    // To early to request
    utils::datetime::MockNowSet(now + std::chrono::seconds(5));
    fsm.SetPosition(*env.context, pos1);
    ASSERT_EQ(env.data.GetCurrentStateStartTime(), now);
    ASSERT_EQ(initial_router_calls, stats.GetRoutesRequested());
  }

  // Now it is a time to try request
  env.router.SetThrow(false);  // Router now is good
  const auto& model_config = env.deps->GetConfig();
  const auto retry_time = now + model_config->GetReturnFromFallbackTimeout() +
                          std::chrono::seconds(1);
  utils::datetime::MockNowSet(retry_time);

  for (auto enabled_return : {false, true}) {
    config.SetEnableReturnFromFallback(enabled_return);
    config.SetEnableAllPointRouting(true);
    env.SetConfig(config);
    fsm.SetPosition(*env.context, pos1);
    if (!enabled_return) {
      ASSERT_EQ(initial_router_calls, stats.GetRoutesRequested());
      ASSERT_EQ(fsm.GetCurrentState()->GetName(),
                fsm.GetStateInstance<FallbackTrackingState>()->GetName());
    } else {
      ASSERT_EQ(initial_router_calls + 1, stats.GetRoutesRequested());
      ASSERT_EQ(fsm.GetCurrentState()->GetName(),
                fsm.GetStateInstance<RouteRequestState>()->GetName());
      /// Wait router response
      auto deadline = engine::Deadline::FromDuration(std::chrono::seconds(3));
      drwi::InputMessage message = env.message_queue.BlockingPop(deadline);
      const auto& route_message = std::get<drwi::RouteMessage>(message.data);
      ASSERT_TRUE(route_message.route);
      fsm.SetRoute(*env.context, *route_message.route, route_message.request_id,
                   std::move(route_message.request_reason),
                   route_message.first_segment_was_rebuilt);

      ASSERT_EQ(fsm.GetCurrentState()->GetName(),
                fsm.GetStateInstance<TrackingState>()->GetName());
      ASSERT_EQ(env.data.GetCurrentStateStartTime(), retry_time);
    }
  }
}

// Test can adjust after failed first try
UTEST(worker_fsm, adjust_after_failed_adjust) {
  drwm::DriverPosition src_pos(10 * lat, 10 * lon, kTransportType, kAdjusted);
  auto dst_pos = MakeDestination({10 * lat, 20 * lon});
  drwm::DriverPosition pos1(11.99999 * lat, 11.99999 * lon, kTransportType,
                            kAdjusted);
  drwm::DriverPosition not_adjustible(12 * lat, 12 * lon, kTransportType,
                                      kAdjusted);
  auto invalid_dst = MakeDestination(pos1);

  const auto driver_id = drwm::DriverId(driver_id::DriverDbid("dbid"),
                                        driver_id::DriverUuid("uuid"));

  drw::test_utils::WorkerFsmEnvironment env(driver_id);

  driver_route_watcher::internal::Config config;
  config.SetEnableAllPointRouting(true);
  env.SetConfig(config);

  // Initial state
  drwi::fsm::RouteWatcherFsm fsm;

  // Set position (gps)
  fsm.SetPosition(*env.context, src_pos);
  // Set destination (start-watch)
  fsm.SetDestination(*env.context, dst_pos);

  // Wait route response appear in message queue
  auto deadline = engine::Deadline::FromDuration(std::chrono::seconds(3));
  drwi::InputMessage message = env.message_queue.BlockingPop(deadline);
  const auto& route_message = std::get<drwi::RouteMessage>(message.data);

  // Received route succesfully, pass it to fsm, should switch to Tracking
  fsm.SetRoute(*env.context, std::move(*route_message.route),
               route_message.request_id,
               std::move(route_message.request_reason),
               route_message.first_segment_was_rebuilt);
  ASSERT_EQ(1ul, env.storage_.outputs_updated);
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<TrackingState>()->GetName());

  // Fail to adjust, enter RouteRebuild state
  fsm.SetPosition(*env.context, not_adjustible);
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<RouteRequestState>()->GetName());
  ASSERT_EQ(1ul, env.storage_.outputs_updated);

  // Receive and set new adjustible to old route position,
  ASSERT_NO_THROW(fsm.SetPosition(*env.context, pos1));

  // There will occure adjustment
  ASSERT_NO_THROW(ProcessRoute(fsm, env));
  ASSERT_EQ(2ul, env.storage_.outputs_updated);
}

// Test on receive position in routerequest state
UTEST(worker_fsm, adjust_in_route_request_recesived_route) {
  drwm::DriverPosition src_pos(10 * lat, 10 * lon, kTransportType, kAdjusted);
  auto dst_pos = MakeDestination({10 * lat, 20 * lon});
  drwm::DriverPosition pos1(10 * lat, 11 * lon, kTransportType,
                            kAdjusted);  // Move along the route
  drwm::DriverPosition pos2(10 * lat, 12 * lon, kTransportType, kAdjusted);
  auto invalid_dst = MakeDestination(pos1);

  const auto driver_id = drwm::DriverId(driver_id::DriverDbid("dbid"),
                                        driver_id::DriverUuid("uuid"));

  drw::test_utils::WorkerFsmEnvironment env(driver_id);

  drwi::Config config;
  config.SetEnableAllPointRouting(true);
  env.SetConfig(config);

  // Initial state
  drwi::fsm::RouteWatcherFsm fsm;

  // Set position (gps)
  fsm.SetPosition(*env.context, src_pos);
  // Set destination (start-watch)
  fsm.SetDestination(*env.context, dst_pos);

  // Wait route response appear in message queue
  auto deadline = engine::Deadline::FromDuration(std::chrono::seconds(3));
  drwi::InputMessage message = env.message_queue.BlockingPop(deadline);
  const auto& route_message = std::get<drwi::RouteMessage>(message.data);
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<RouteRequestState>()->GetName());

  // Receive new position (later will provoke adjust this position to
  // recieved route)
  fsm.SetPosition(*env.context, pos2);
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<RouteRequestState>()->GetName());
  ASSERT_EQ(0ul, env.storage_.outputs_updated);

  // Received route succesfully, pass it to fsm, should switch to Tracking
  fsm.SetRoute(*env.context, std::move(*route_message.route),
               route_message.request_id,
               std::move(route_message.request_reason),
               route_message.first_segment_was_rebuilt);
  ASSERT_EQ(1ul, env.storage_.outputs_updated);

  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<TrackingState>()->GetName());
}

UTEST(worker_fsm, multi_destination) {
  const auto& service0 = drwm::ServiceId("service0");
  const auto& service1 = drwm::ServiceId("service1");
  const auto& service2 = drwm::ServiceId("service2");
  drwm::DriverPosition src_pos(10 * lat, 10 * lon, kTransportType, kAdjusted);
  drwm::DriverPosition pos1(10 * lat, 11 * lon, kTransportType,
                            kAdjusted);  // Move along the route
  auto dst_pos0 = MakeDestination({10 * lat, 20 * lon}, service0);
  auto dst_pos1 = MakeDestination({10 * lat, 21 * lon}, service1);
  auto dst_pos2 = MakeDestination({10 * lat, 22 * lon}, service2);
  auto invalid_dst = MakeDestination(pos1);

  drwm::DriverPosition pos2(10 * lat, 12 * lon, kTransportType, kAdjusted);
  const auto driver_id = drwm::DriverId(driver_id::DriverDbid("dbid"),
                                        driver_id::DriverUuid("uuid"));

  drw::test_utils::WorkerFsmEnvironment env(driver_id);
  drwi::Config new_config;
  new_config.SetServicePriorityConfig({
      {"service0", 10},
      {"service1", 100},
      {"service2", 1},
  });
  new_config.SetEnableAllPointRouting(true);
  env.SetConfig(new_config);

  // Initial state
  drwi::fsm::RouteWatcherFsm fsm;

  {
    // Wait data
    {
      // Set destination (start-watch)
      fsm.SetDestination(*env.context, dst_pos0);
      ASSERT_EQ(fsm.GetCurrentState()->GetName(),
                fsm.GetStateInstance<WaitDataState>()->GetName());
      const auto& dst_points = env.data.GetTrackedDestinationPoints();
      ASSERT_FALSE(dst_points.empty());
      ASSERT_TRUE(drwi::IsEqual(dst_points.back().GetPosition(),
                                dst_pos0.ExpressDestinationAsPosition()));
    }
    {
      // Set low-priority destination (start-watch)
      fsm.SetDestination(*env.context, dst_pos2);
      ASSERT_EQ(fsm.GetCurrentState()->GetName(),
                fsm.GetStateInstance<WaitDataState>()->GetName());
      const auto& dst_points = env.data.GetTrackedDestinationPoints();
      // last point changed (because low-priority points go to end)
      ASSERT_TRUE(drwi::IsEqual(dst_points.back().GetPosition(),
                                dst_pos2.ExpressDestinationAsPosition()));
    }
    {
      // Set high-priority destination (start-watch)
      fsm.SetDestination(*env.context, dst_pos1);
      ASSERT_EQ(fsm.GetCurrentState()->GetName(),
                fsm.GetStateInstance<WaitDataState>()->GetName());
      const auto& dst_points = env.data.GetTrackedDestinationPoints();
      // last point not changed (because high-priority points go to begin)
      ASSERT_TRUE(drwi::IsEqual(dst_points.back().GetPosition(),
                                dst_pos2.ExpressDestinationAsPosition()));
      ASSERT_TRUE(drwi::IsEqual(dst_points.front().GetPosition(),
                                dst_pos1.ExpressDestinationAsPosition()));
    }
  }

  // Set position (gps)
  fsm.SetPosition(*env.context, src_pos);
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<RouteRequestState>()->GetName());
  {
    // Reset destiantions in request state
    {
      fsm.ResetDestination(*env.context, dst_pos1);
      ASSERT_EQ(fsm.GetCurrentState()->GetName(),
                fsm.GetStateInstance<RouteRequestState>()->GetName());
      ASSERT_FALSE(env.data.GetTrackedDestinationPoints().empty());
      const auto& first_point = env.data.GetTrackedDestinationPoints()[0];
      // Changed to next destination by priority
      ASSERT_TRUE(drwi::IsEqual(first_point.GetPosition(),
                                dst_pos0.ExpressDestinationAsPosition()));
    }
    {
      fsm.ResetDestination(*env.context, dst_pos2);
      ASSERT_EQ(fsm.GetCurrentState()->GetName(),
                fsm.GetStateInstance<RouteRequestState>()->GetName());
      ASSERT_FALSE(env.data.GetTrackedDestinationPoints().empty());
      const auto& first_point = env.data.GetTrackedDestinationPoints()[0];
      // Changed to next destination by priority
      ASSERT_TRUE(drwi::IsEqual(first_point.GetPosition(),
                                dst_pos0.ExpressDestinationAsPosition()));
    }
    {
      fsm.ResetDestination(*env.context, dst_pos0);
      // There are no destinations anymore
      ASSERT_EQ(fsm.GetCurrentState()->GetName(),
                fsm.GetStateInstance<WaitDataState>()->GetName());
      ASSERT_TRUE(env.data.GetTrackedDestinationPoints().empty());
    }
  }

  fsm.SetDestination(*env.context, dst_pos0);
  fsm.SetDestination(*env.context, dst_pos2);
  fsm.SetDestination(*env.context, dst_pos1);

  {
    ASSERT_EQ(fsm.GetCurrentState()->GetName(),
              fsm.GetStateInstance<RouteRequestState>()->GetName());
  }

  {
    auto deadline = engine::Deadline::FromDuration(std::chrono::seconds(3));
    // We set 3 destinations and request route 3 times, so first 2 requests are
    // obsolete.
    for (size_t i = 0; i < 3; ++i) {
      ASSERT_EQ(fsm.GetCurrentState()->GetName(),
                fsm.GetStateInstance<RouteRequestState>()->GetName());
      drwi::InputMessage message = env.message_queue.BlockingPop(deadline);
      const auto& route_message = std::get<drwi::RouteMessage>(message.data);
      fsm.SetRoute(*env.context, std::move(*route_message.route),
                   route_message.request_id,
                   std::move(route_message.request_reason),
                   route_message.first_segment_was_rebuilt);
    }
    ASSERT_EQ(fsm.GetCurrentState()->GetName(),
              fsm.GetStateInstance<TrackingState>()->GetName());
  }

  {
    // Reset destiantions in tracking state
    fsm.ResetDestination(*env.context, dst_pos2);
    ASSERT_EQ(fsm.GetCurrentState()->GetName(),
              fsm.GetStateInstance<RouteRequestState>()->GetName());
    ASSERT_FALSE(env.data.GetTrackedDestinationPoints().empty());
    const auto& first_point = env.data.GetTrackedDestinationPoints()[0];
    // Does not changed (dst_pos2 was background destination)
    ASSERT_TRUE(drwi::IsEqual(first_point.GetPosition(),
                              dst_pos1.ExpressDestinationAsPosition()));
  }
  {
    fsm.ResetDestination(*env.context, dst_pos1);
    ASSERT_EQ(fsm.GetCurrentState()->GetName(),
              fsm.GetStateInstance<RouteRequestState>()->GetName());
    ASSERT_FALSE(env.data.GetTrackedDestinationPoints().empty());
    const auto& first_point = env.data.GetTrackedDestinationPoints()[0];
    // Changed to next destination by priority
    ASSERT_TRUE(drwi::IsEqual(first_point.GetPosition(),
                              dst_pos0.ExpressDestinationAsPosition()));
  }

  {
    try {
      for (size_t i = 0; i < 2; ++i) {
        auto deadline = engine::Deadline::FromDuration(std::chrono::seconds(3));
        drwi::InputMessage message = env.message_queue.BlockingPop(deadline);
        const auto& route_message = std::get<drwi::RouteMessage>(message.data);
        // Received route succesfully, pass it to fsm, should switch to Tracking
        fsm.SetRoute(*env.context, std::move(*route_message.route),
                     route_message.request_id,
                     std::move(route_message.request_reason),
                     route_message.first_segment_was_rebuilt);
      }
    } catch (const BlockingPopTimeout&) {
    }

    ASSERT_EQ(fsm.GetCurrentState()->GetName(),
              fsm.GetStateInstance<TrackingState>()->GetName());
  }

  {
    // Set low-priority destination (start-watch)
    fsm.SetDestination(*env.context, dst_pos2);
    ASSERT_EQ(fsm.GetCurrentState()->GetName(),
              fsm.GetStateInstance<RouteRequestState>()->GetName());
    ASSERT_FALSE(env.data.GetTrackedDestinationPoints().empty());
    const auto& first_point = env.data.GetTrackedDestinationPoints()[0];
    // Does not changed
    ASSERT_TRUE(drwi::IsEqual(first_point.GetPosition(),
                              dst_pos0.ExpressDestinationAsPosition()));
  }
  {
    // Set high-priority destination (start-watch)
    fsm.SetDestination(*env.context, dst_pos1);
    ASSERT_EQ(fsm.GetCurrentState()->GetName(),
              fsm.GetStateInstance<RouteRequestState>()->GetName());
    ASSERT_FALSE(env.data.GetTrackedDestinationPoints().empty());
    const auto& first_point = env.data.GetTrackedDestinationPoints()[0];
    // Changed to new destiantion
    ASSERT_TRUE(drwi::IsEqual(first_point.GetPosition(),
                              dst_pos1.ExpressDestinationAsPosition()));
  }

  {
    auto deadline = engine::Deadline::FromDuration(std::chrono::seconds(3));
    drwi::InputMessage message = env.message_queue.BlockingPop(deadline);
    const auto& route_message = std::get<drwi::RouteMessage>(message.data);
    // Received route succesfully, pass it to fsm, should switch to Tracking
    fsm.SetRoute(*env.context, std::move(*route_message.route),
                 route_message.request_id,
                 std::move(route_message.request_reason),
                 route_message.first_segment_was_rebuilt);
    ASSERT_EQ(fsm.GetCurrentState()->GetName(),
              fsm.GetStateInstance<TrackingState>()->GetName());
  }

  {  // Reset all destinations tracking state
    {
      fsm.ResetDestination(*env.context, dst_pos2);
      ASSERT_EQ(fsm.GetCurrentState()->GetName(),
                fsm.GetStateInstance<RouteRequestState>()->GetName());
      ASSERT_FALSE(env.data.GetTrackedDestinationPoints().empty());
      const auto& first_point = env.data.GetTrackedDestinationPoints()[0];
      // Does not changed (dst_pos2 was background destination)
      ASSERT_TRUE(drwi::IsEqual(first_point.GetPosition(),
                                dst_pos1.ExpressDestinationAsPosition()));
    }
    {
      fsm.ResetDestination(*env.context, dst_pos0);
      ASSERT_EQ(fsm.GetCurrentState()->GetName(),
                fsm.GetStateInstance<RouteRequestState>()->GetName());
      ASSERT_FALSE(env.data.GetTrackedDestinationPoints().empty());
      const auto& first_point = env.data.GetTrackedDestinationPoints()[0];
      // Does not changed (dst_pos0 was background destination)
      ASSERT_TRUE(drwi::IsEqual(first_point.GetPosition(),
                                dst_pos1.ExpressDestinationAsPosition()));
    }
    {
      fsm.ResetDestination(*env.context, dst_pos1);
      ASSERT_EQ(fsm.GetCurrentState()->GetName(),
                fsm.GetStateInstance<WaitDataState>()->GetName());
      ASSERT_TRUE(env.data.GetTrackedDestinationPoints().empty());
    }
  }
}

UTEST(worker_fsm, rebuild_old_route) {
  /// Test case when passed enough time
  /// (model_config->GetRebuilOldRouteTimeout()) to rebild route we have to
  /// request route again
  drwm::DriverPosition src_pos(10 * lat, 10 * lon, kTransportType, kAdjusted);
  drwm::DriverPosition pos1(10 * lat, 11 * lon, kTransportType,
                            kAdjusted);  // Move along the route
  auto dst_pos = MakeDestination({10 * lat, 20 * lon});

  // turn from route by 90 deg.
  drwm::DriverPosition pos2(11 * lat, 11 * lon, kTransportType, kAdjusted);
  const auto driver_id = drwm::DriverId(driver_id::DriverDbid("dbid"),
                                        driver_id::DriverUuid("uuid"));
  drw::test_utils::WorkerFsmEnvironment env(driver_id);

  driver_route_watcher::internal::Config config;
  config.SetEnableAllPointRouting(true);
  env.SetConfig(config);

  // Initial state
  drwi::fsm::RouteWatcherFsm fsm;
  fsm.SetPosition(*env.context, src_pos);
  fsm.SetDestination(*env.context, dst_pos);
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<RouteRequestState>()->GetName());

  // Wait route response appear in message queue
  auto deadline = engine::Deadline::FromDuration(std::chrono::seconds(3));
  drwi::InputMessage message = env.message_queue.BlockingPop(deadline);
  const auto& route_message = std::get<drwi::RouteMessage>(message.data);

  const auto now = utils::datetime::Now();
  utils::datetime::MockNowSet(now);
  // Received route failed, pass it to fsm, should switch to FalbackTracking
  fsm.SetRoute(*env.context, *route_message.route, route_message.request_id,
               std::move(route_message.request_reason),
               route_message.first_segment_was_rebuilt);
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<TrackingState>()->GetName());
  ASSERT_TRUE(env.storage_.GetFsmRestoreData(driver_id));
  ASSERT_EQ(env.storage_.GetFsmRestoreData(driver_id)->current_state,
            drwm::FsmStateType::kTracking);
  ASSERT_EQ(env.data.GetCurrentStateStartTime(), now);

  auto& stats = env.context->GetStats();
  const auto initial_router_calls = stats.GetRoutesRequested();

  // Now it is a time to try request
  const auto& model_config = env.deps->GetConfig();
  const auto retry_time =
      now + model_config->GetRebuildOldRouteTimeout() + std::chrono::seconds(1);
  utils::datetime::MockNowSet(retry_time);

  config.SetEnableReturnFromFallback(true);
  config.SetEnableAllPointRouting(true);
  env.SetConfig(config);
  fsm.SetPosition(*env.context, pos1);

  ASSERT_TRUE(env.storage_.GetFsmRestoreData(driver_id));
  {
    /// no request cause eta less than GetRebuildOldRouteMinEta
    ASSERT_EQ(initial_router_calls, stats.GetRoutesRequested());
    ASSERT_EQ(fsm.GetCurrentState()->GetName(),
              fsm.GetStateInstance<TrackingState>()->GetName());
  }

  /// change config to allow rebuild
  config.SetRebuildOldRouteMinEta(std::chrono::seconds(30));
  config.SetEnableAllPointRouting(true);
  env.SetConfig(config);
  fsm.SetPosition(*env.context, pos1);

  {
    ASSERT_EQ(initial_router_calls + 1, stats.GetRoutesRequested());
    ASSERT_EQ(fsm.GetCurrentState()->GetName(),
              fsm.GetStateInstance<RouteRebuildState>()->GetName());
    /// Wait router response
    auto deadline = engine::Deadline::FromDuration(std::chrono::seconds(3));
    drwi::InputMessage message = env.message_queue.BlockingPop(deadline);
    const auto& route_message = std::get<drwi::RouteMessage>(message.data);
    ASSERT_TRUE(route_message.route);
    fsm.SetRoute(*env.context, *route_message.route, route_message.request_id,
                 std::move(route_message.request_reason),
                 route_message.first_segment_was_rebuilt);

    ASSERT_TRUE(env.storage_.GetFsmRestoreData(driver_id));
    ASSERT_EQ(env.storage_.GetFsmRestoreData(driver_id)->current_state,
              drwm::FsmStateType::kTracking);
    ASSERT_EQ(fsm.GetCurrentState()->GetName(),
              fsm.GetStateInstance<TrackingState>()->GetName());
    ASSERT_EQ(env.data.GetCurrentStateStartTime(), retry_time);
  }
}

UTEST(worker_fsm, rebuild_old_route_by_experiment) {
  /// Test case when passed enough time
  /// (model_config->GetRebuilOldRouteTimeout()) to rebild route we have to
  /// request route again
  drwm::DriverPosition src_pos(10 * lat, 10 * lon, kTransportType, kAdjusted);
  drwm::DriverPosition pos1(10 * lat, 11 * lon, kTransportType,
                            kAdjusted);  // Move along the route
  auto dst_pos = MakeDestination({10 * lat, 20 * lon});

  // turn from route by 90 deg.
  drwm::DriverPosition pos2(11 * lat, 11 * lon, kTransportType, kAdjusted);
  const auto driver_id = drwm::DriverId(driver_id::DriverDbid("dbid"),
                                        driver_id::DriverUuid("uuid"));
  drw::test_utils::WorkerFsmEnvironment env(driver_id);

  driver_route_watcher::internal::Config config;
  config.SetEnableAllPointRouting(true);
  env.SetConfig(config);

  // Initial state
  drwi::fsm::RouteWatcherFsm fsm;
  fsm.SetPosition(*env.context, src_pos);
  fsm.SetDestination(*env.context, dst_pos);
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<RouteRequestState>()->GetName());

  // Wait route response appear in message queue
  auto deadline = engine::Deadline::FromDuration(std::chrono::seconds(3));
  drwi::InputMessage message = env.message_queue.BlockingPop(deadline);
  const auto& route_message = std::get<drwi::RouteMessage>(message.data);

  const auto now = utils::datetime::Now();
  utils::datetime::MockNowSet(now);
  // Received route failed, pass it to fsm, should switch to FalbackTracking
  fsm.SetRoute(*env.context, *route_message.route, route_message.request_id,
               std::move(route_message.request_reason),
               route_message.first_segment_was_rebuilt);
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<TrackingState>()->GetName());
  auto output = env.storage_.GetFsmRestoreData(driver_id);
  ASSERT_TRUE(output);
  ASSERT_EQ(output->current_state, drwm::FsmStateType::kTracking);
  ASSERT_EQ(env.data.GetCurrentStateStartTime(), now);

  auto& stats = env.context->GetStats();
  const auto initial_router_calls = stats.GetRoutesRequested();

  // Now it is a time to try request
  const auto& model_config = env.deps->GetConfig();
  const auto retry_time =
      now + model_config->GetRebuildOldRouteTimeout() + std::chrono::seconds(1);
  utils::datetime::MockNowSet(retry_time);

  config.SetEnableReturnFromFallback(true);
  config.SetEnableAllPointRouting(true);
  env.SetConfig(config);
  fsm.SetPosition(*env.context, pos1);
  output = env.storage_.GetFsmRestoreData(driver_id);
  ASSERT_TRUE(output);
  {
    /// no request cause eta less than GetRebuildOldRouteMinEta
    ASSERT_EQ(initial_router_calls, stats.GetRoutesRequested());
    ASSERT_EQ(output->current_state, drwm::FsmStateType::kTracking);
  }

  /// change experiment to allow rebuild
  auto& exp = dynamic_cast<driver_route_watcher::test_utils::TestExperiments&>(
      env.deps->GetExperiments());
  exp.SetResult(driver_route_watcher::internal::ExperimentsBase::Values{
      std::chrono::seconds(30), std::nullopt});

  fsm.SetPosition(*env.context, pos1);
  {
    ASSERT_EQ(initial_router_calls + 1, stats.GetRoutesRequested());
    ASSERT_EQ(fsm.GetCurrentState()->GetName(),
              fsm.GetStateInstance<RouteRebuildState>()->GetName());
    /// Wait router response
    auto deadline = engine::Deadline::FromDuration(std::chrono::seconds(3));
    drwi::InputMessage message = env.message_queue.BlockingPop(deadline);
    const auto& route_message = std::get<drwi::RouteMessage>(message.data);
    ASSERT_TRUE(route_message.route);
    fsm.SetRoute(*env.context, *route_message.route, route_message.request_id,
                 std::move(route_message.request_reason),
                 route_message.first_segment_was_rebuilt);

    const auto& output = env.storage_.GetFsmRestoreData(driver_id);
    ASSERT_TRUE(output);
    ASSERT_EQ(output->current_state, drwm::FsmStateType::kTracking);
    ASSERT_EQ(env.data.GetCurrentStateStartTime(), retry_time);
  }
}

UTEST(worker_fsm, failed_to_rebuild_old_route) {
  /// Test case when passed enough time
  /// (model_config->GetRebuilOldRouteTimeout()) to rebild route we have to
  /// request route again but failed to get new route, so we have to use old
  drwm::DriverPosition src_pos(10 * lat, 10 * lon, kTransportType, kAdjusted);
  drwm::DriverPosition pos1(10 * lat, 11 * lon, kTransportType,
                            kAdjusted);  // Move along the route
  auto dst_pos = MakeDestination({10 * lat, 20 * lon});

  // turn from route by 90 deg.
  drwm::DriverPosition pos2(11 * lat, 11 * lon, kTransportType, kAdjusted);
  const auto driver_id = drwm::DriverId(driver_id::DriverDbid("dbid"),
                                        driver_id::DriverUuid("uuid"));
  drw::test_utils::WorkerFsmEnvironment env(driver_id);

  drwi::Config config;
  config.SetEnableAllPointRouting(true);
  env.SetConfig(config);

  // Initial state
  drwi::fsm::RouteWatcherFsm fsm;
  fsm.SetPosition(*env.context, src_pos);
  fsm.SetDestination(*env.context, dst_pos);
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<RouteRequestState>()->GetName());

  // Wait route response appear in message queue
  auto deadline = engine::Deadline::FromDuration(std::chrono::seconds(3));
  drwi::InputMessage message = env.message_queue.BlockingPop(deadline);
  const auto& route_message = std::get<drwi::RouteMessage>(message.data);

  const auto now = utils::datetime::Now();
  utils::datetime::MockNowSet(now);
  // Received route failed, pass it to fsm, should switch to FalbackTracking
  fsm.SetRoute(*env.context, *route_message.route, route_message.request_id,
               std::move(route_message.request_reason),
               route_message.first_segment_was_rebuilt);
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<TrackingState>()->GetName());
  const auto& output = env.storage_.GetFsmRestoreData(driver_id);
  ASSERT_TRUE(output);
  ASSERT_EQ(output->current_state, drwm::FsmStateType::kTracking);
  ASSERT_EQ(env.data.GetCurrentStateStartTime(), now);
  ASSERT_EQ(output->current_state_start_time, now);

  auto& stats = env.context->GetStats();
  const auto initial_router_calls = stats.GetRoutesRequested();

  // Now it is a time to try request
  const auto& model_config = env.deps->GetConfig();
  const auto retry_time =
      now + model_config->GetRebuildOldRouteTimeout() + std::chrono::seconds(1);
  utils::datetime::MockNowSet(retry_time);

  config.SetEnableReturnFromFallback(true);
  config.SetRebuildOldRouteMinEta(std::chrono::seconds(30));
  config.SetEnableAllPointRouting(true);
  env.SetConfig(config);
  env.router.SetThrow(true);  // break router, so we fail to get new route
  fsm.SetPosition(*env.context, pos1);
  {
    ASSERT_EQ(initial_router_calls + 1, stats.GetRoutesRequested());
    ASSERT_EQ(fsm.GetCurrentState()->GetName(),
              fsm.GetStateInstance<RouteRebuildState>()->GetName());
    /// Wait router response
    auto deadline = engine::Deadline::FromDuration(std::chrono::seconds(3));
    drwi::InputMessage message = env.message_queue.BlockingPop(deadline);
    const auto& route_message =
        std::get<drwi::RouteFailedMessage>(message.data);
    fsm.SetRouteFailed(*env.context, route_message.request_id,
                       route_message.reason,
                       std::move(route_message.request_reason));

    const auto& output = env.storage_.GetFsmRestoreData(driver_id);
    ASSERT_TRUE(output);
    ASSERT_EQ(output->current_state, drwm::FsmStateType::kTracking);
    ASSERT_EQ(env.data.GetCurrentStateStartTime(), retry_time);
  }
}

UTEST(worker_fsm, order_without_B) {
  drwm::DriverPosition src_pos(10 * lat, 10 * lon, kTransportType, kAdjusted);
  auto unknown_dst = MakeUnknownDestination();
  ASSERT_TRUE(unknown_dst.IsUnknownDestination());
  drwm::DriverPosition pos1(10 * lat, 11 * lon, kTransportType,
                            kAdjusted);  // Move along the route
  auto invalid_dst = MakeDestination(pos1);

  drwm::DriverPosition pos2(10 * lat, 12 * lon, kTransportType, kAdjusted);
  const auto driver_id = drwm::DriverId(driver_id::DriverDbid("dbid"),
                                        driver_id::DriverUuid("uuid"));

  drw::test_utils::WorkerFsmEnvironment env(driver_id);

  drwi::Config config;
  config.SetEnableAllPointRouting(true);
  env.SetConfig(config);

  // Initial state
  drwi::fsm::RouteWatcherFsm fsm;
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<WaitDataState>()->GetName());

  // Set destination (start-watch)
  fsm.SetDestination(*env.context, unknown_dst);
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<WaitDataState>()->GetName());
  ASSERT_EQ(0ul, env.storage_.outputs_updated);

  // Set position (gps)
  fsm.SetPosition(*env.context, src_pos);
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<UnknownDestinationState>()->GetName());
  ASSERT_EQ(1ul, env.storage_.outputs_updated);

  {
    // Now watched
    auto output_ptr = env.output[driver_id]->Lock();
    ASSERT_FALSE(output_ptr->IsDeleted());
  }
  {
    const auto& output = env.storage_.GetFsmRestoreData(driver_id);
    ASSERT_TRUE(output);
  }

  // No route requests should happend
  auto deadline = engine::Deadline::FromDuration(std::chrono::seconds(3));
  ASSERT_THROW(env.message_queue.BlockingPop(deadline), BlockingPopTimeout);
  ASSERT_EQ(0ul, env.storage_.routes_stored);

  {
    // Has TrackingState output now
    // Values are dummy, should be changed after AdjusterIntegration
    auto output_ptr = env.output[driver_id]->Lock();
    ASSERT_FALSE(output_ptr->IsDeleted());
    const auto& output_destination = output_ptr->GetDestination();
    ASSERT_TRUE(output_destination.IsUnknownDestination());
    ASSERT_EQ(output_destination.service_id.GetUnderlying(), "some-service-id");
    ASSERT_EQ(output_destination.metainfo, "some-meta-info");
  }
  {
    auto output = env.storage_.GetFsmRestoreData(driver_id);
    ASSERT_TRUE(output);
    ASSERT_EQ(output->current_state, drwm::FsmStateType::kUnknownDestination);
  }

  // Receive some positions in tracking state
  for (const auto& pos : {pos1, pos2}) {
    fsm.SetPosition(*env.context, pos);
    ASSERT_EQ(fsm.GetCurrentState()->GetName(),
              fsm.GetStateInstance<UnknownDestinationState>()->GetName());
  }
  ASSERT_EQ(3ul, env.storage_.outputs_updated);

  {
    // Has TrackingState output now
    auto output_ptr = env.output[driver_id]->Lock();
    ASSERT_FALSE(output_ptr->IsDeleted());
    ASSERT_TRUE(output_ptr->GetDestination().IsUnknownDestination());
  }
  {
    auto output = env.storage_.GetFsmRestoreData(driver_id);
    ASSERT_TRUE(output);
    ASSERT_EQ(output->current_state, drwm::FsmStateType::kUnknownDestination);
  }

  // Try reset destination with invalid position (not actualy watching)
  fsm.ResetDestination(*env.context, invalid_dst);
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<UnknownDestinationState>()->GetName());
  ASSERT_EQ(3ul, env.storage_.outputs_updated);

  // Reset destination (pass correct destination)
  fsm.ResetDestination(*env.context, unknown_dst);
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<WaitDataState>()->GetName());
  ASSERT_EQ(1ul, env.storage_.outputs_cleared);
}

UTEST(worker_fsm, reset_old_destination) {
  /// Test case when passed enough time
  /// (model_config->GetOldWatchTimeout() and
  ///  model_config->GetOldWatchRouteMultiplier()) to reset watch we have to
  /// reset current destination
  const auto now = utils::datetime::Now();
  utils::datetime::MockNowSet(now);

  drwm::DriverPosition src_pos(10 * lat, 10 * lon, kTransportType, kAdjusted);
  drwm::DriverPosition pos1(10 * lat, 11 * lon, kTransportType,
                            kAdjusted);  // Move along the route
  drwm::DriverPosition pos2(10 * lat, 12 * lon, kTransportType, kAdjusted);
  auto dst_pos = MakeDestination({10 * lat, 20 * lon}, now);

  const auto driver_id = drwm::DriverId(driver_id::DriverDbid("dbid"),
                                        driver_id::DriverUuid("uuid"));
  drw::test_utils::WorkerFsmEnvironment env(driver_id);

  drwi::Config config;
  config.SetEnableAllPointRouting(true);
  env.SetConfig(config);

  // Initial state
  drwi::fsm::RouteWatcherFsm fsm;
  fsm.SetPosition(*env.context, src_pos);
  fsm.SetDestination(*env.context, dst_pos);

  // Wait route response appear in message queue
  auto deadline = engine::Deadline::FromDuration(std::chrono::seconds(3));
  drwi::InputMessage message = env.message_queue.BlockingPop(deadline);
  const auto& route_message = std::get<drwi::RouteMessage>(message.data);

  fsm.SetRoute(*env.context, *route_message.route, route_message.request_id,
               std::move(route_message.request_reason),
               route_message.first_segment_was_rebuilt);
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<TrackingState>()->GetName());
  const auto& output = env.storage_.GetFsmRestoreData(driver_id);
  ASSERT_TRUE(output);
  ASSERT_EQ(output->current_state, drwm::FsmStateType::kTracking);
  ASSERT_EQ(env.data.GetCurrentStateStartTime(), now);
  ASSERT_EQ(output->current_state_start_time, now);

  config.SetEnableRebuildOldRoute(false);
  config.SetEnableAllPointRouting(true);
  env.SetConfig(config);

  auto& stats = env.context->GetStats();
  const auto& model_config = env.deps->GetConfig();

  /// time when it is need to reset old watch
  const auto reset_time =
      now + model_config->GetOldWatchTimeout() + std::chrono::seconds(1);
  utils::datetime::MockNowSet(reset_time);

  ASSERT_EQ(0ull, stats.GetResetOldWatch());
  fsm.SetPosition(*env.context, pos1);
  {
    auto deadline = engine::Deadline::FromDuration(std::chrono::seconds(3));
    drwi::InputMessage message = env.message_queue.BlockingPop(deadline);
    const auto& stop_message = std::get<drwi::StopWatchMessage>(message.data);
    fsm.ResetDestination(*env.context, stop_message.expected_destination);
    ASSERT_EQ(fsm.GetCurrentState()->GetName(),
              fsm.GetStateInstance<WaitDataState>()->GetName());
  }
  ASSERT_EQ(1ull, stats.GetResetOldWatch());
  ASSERT_EQ(1ul, env.storage_.outputs_cleared);
}

UTEST(worker_fsm, reset_old_multi_destination_older) {
  /// Test case when passed enough time
  /// (model_config->GetOldWatchTimeout()) to reset watch we have to
  /// reset current destination and background destination cause it is older
  /// than current
  const auto now = utils::datetime::Now();
  utils::datetime::MockNowSet(now);

  drwm::DriverPosition src_pos(10 * lat, 10 * lon, kTransportType, kAdjusted);
  drwm::DriverPosition pos1(10 * lat, 11 * lon, kTransportType,
                            kAdjusted);  // Move along the route
  drwm::DriverPosition pos2(10 * lat, 12 * lon, kTransportType, kAdjusted);
  auto dst_pos = MakeDestination({10 * lat, 20 * lon}, now, "Service0");
  /// Second destination older than current. So it has to be reseted too
  const auto other_destination_start = now - std::chrono::seconds(10);
  auto other_pos = MakeDestination({10 * lat, 20 * lon},
                                   other_destination_start, "Service1");

  const auto driver_id = drwm::DriverId(driver_id::DriverDbid("dbid"),
                                        driver_id::DriverUuid("uuid"));
  drw::test_utils::WorkerFsmEnvironment env(driver_id);

  drwi::Config config;
  config.SetEnableAllPointRouting(true);
  env.SetConfig(config);

  // Initial state
  drwi::fsm::RouteWatcherFsm fsm;
  fsm.SetPosition(*env.context, src_pos);
  fsm.SetDestination(*env.context, other_pos);
  fsm.SetDestination(*env.context, dst_pos);

  try {
    for (size_t i = 0; i < 2; ++i) {
      // Wait route response appear in message queue
      auto deadline = engine::Deadline::FromDuration(std::chrono::seconds(3));
      drwi::InputMessage message = env.message_queue.BlockingPop(deadline);
      const auto& route_message = std::get<drwi::RouteMessage>(message.data);

      fsm.SetRoute(*env.context, *route_message.route, route_message.request_id,
                   std::move(route_message.request_reason),
                   route_message.first_segment_was_rebuilt);
    }
  } catch (const BlockingPopTimeout&) {
  }
  ASSERT_TRUE(env.storage_.GetFsmRestoreData(driver_id));
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<TrackingState>()->GetName());

  config.SetEnableRebuildOldRoute(false);
  config.SetEnableAllPointRouting(true);
  env.SetConfig(config);

  auto& stats = env.context->GetStats();
  const auto& model_config = env.deps->GetConfig();

  /// time when it is need to reset old watch
  const auto reset_time =
      now + model_config->GetOldWatchTimeout() + std::chrono::seconds(1);
  utils::datetime::MockNowSet(reset_time);
  ASSERT_EQ(0ull, stats.GetResetOldWatch());

  fsm.SetPosition(*env.context, pos1);
  {
    // requested 2 stop messages
    auto deadline = engine::Deadline::FromDuration(std::chrono::seconds(3));
    drwi::InputMessage message = env.message_queue.BlockingPop(deadline);
    const auto first_stop_message =
        std::get<drwi::StopWatchMessage>(message.data);
    message = env.message_queue.BlockingPop(deadline);
    const auto second_stop_message =
        std::get<drwi::StopWatchMessage>(message.data);

    // first ResetDestination will request route
    fsm.ResetDestination(*env.context, first_stop_message.expected_destination);
    message = env.message_queue.BlockingPop(deadline);
    std::ignore = std::get<drwi::RouteMessage>(message.data);

    // second ResetDestination will transit fsm to wait_data_state
    fsm.ResetDestination(*env.context,
                         second_stop_message.expected_destination);
    ASSERT_EQ(fsm.GetCurrentState()->GetName(),
              fsm.GetStateInstance<WaitDataState>()->GetName());

    ASSERT_EQ(2ull, stats.GetResetOldWatch());
  }
}

UTEST(worker_fsm, reset_old_multi_destination_newer) {
  /// Test case when passed enough time
  /// (model_config->GetOldWatchTimeout()) to reset watch we have to
  /// reset current destination but leave background destination cause it is
  /// newer than current
  const auto now = utils::datetime::Now();
  utils::datetime::MockNowSet(now);

  drwm::DriverPosition src_pos(10 * lat, 10 * lon, kTransportType, kAdjusted);
  drwm::DriverPosition pos1(10 * lat, 11 * lon, kTransportType,
                            kAdjusted);  // Move along the route
  drwm::DriverPosition pos2(10 * lat, 12 * lon, kTransportType, kAdjusted);
  auto dst_pos = MakeDestination({10 * lat, 20 * lon}, now, "Service0");
  /// Second destination newer than current. So it has to replace current
  /// destination and become active
  const auto other_destination_start = now + std::chrono::seconds(10);
  auto other_pos = MakeDestination({22 * lat, 33 * lon},
                                   other_destination_start, "Service1");

  const auto driver_id = drwm::DriverId(driver_id::DriverDbid("dbid"),
                                        driver_id::DriverUuid("uuid"));
  drw::test_utils::WorkerFsmEnvironment env(driver_id);

  drwi::Config config;
  config.SetEnableAllPointRouting(true);
  env.SetConfig(config);

  // Initial state
  drwi::fsm::RouteWatcherFsm fsm;
  fsm.SetPosition(*env.context, src_pos);
  fsm.SetDestination(*env.context, other_pos);
  fsm.SetDestination(*env.context, dst_pos);

  // Wait route response appear in message queue
  auto deadline = engine::Deadline::FromDuration(std::chrono::seconds(3));
  drwi::InputMessage message = env.message_queue.BlockingPop(deadline);
  const auto& route_message = std::get<drwi::RouteMessage>(message.data);

  fsm.SetRoute(*env.context, *route_message.route, route_message.request_id,
               std::move(route_message.request_reason),
               route_message.first_segment_was_rebuilt);
  ASSERT_TRUE(env.storage_.GetFsmRestoreData(driver_id));

  config.SetEnableRebuildOldRoute(false);
  config.SetEnableAllPointRouting(true);
  env.SetConfig(config);

  auto& stats = env.context->GetStats();
  const auto& model_config = env.deps->GetConfig();

  /// time when it is need to reset old watch
  const auto reset_time =
      now + model_config->GetOldWatchTimeout() + std::chrono::seconds(1);
  utils::datetime::MockNowSet(reset_time);

  ASSERT_EQ(0ull, stats.GetResetOldWatch());
  fsm.SetPosition(*env.context, pos1);
  {
    auto deadline = engine::Deadline::FromDuration(std::chrono::seconds(3));
    drwi::InputMessage message = env.message_queue.BlockingPop(deadline);
    const auto& stop_message = std::get<drwi::StopWatchMessage>(message.data);
    fsm.ResetDestination(*env.context, stop_message.expected_destination);
    ASSERT_EQ(fsm.GetCurrentState()->GetName(),
              fsm.GetStateInstance<RouteRequestState>()->GetName());
  }
  {
    /// Wait route requester task to prevent ub(read after free) in tests
    auto deadline = engine::Deadline::FromDuration(std::chrono::seconds(3));
    env.message_queue.BlockingPop(deadline);
  }
  ASSERT_FALSE(env.data.GetTrackedDestinationPoints().empty());
  const auto& first_point = env.data.GetTrackedDestinationPoints()[0];
  ASSERT_EQ(first_point.GetServiceId().GetUnderlying(), "Service1");

  ASSERT_EQ(1ull, stats.GetResetOldWatch());
  ASSERT_EQ(0ul, env.storage_.outputs_cleared);
}

UTEST(worker_fsm, failed_route_on_failed_adjust) {
  const auto driver_id = drwm::DriverId(driver_id::DriverDbid("dbid"),
                                        driver_id::DriverUuid("uuid"));
  drw::test_utils::WorkerFsmEnvironment env(driver_id);
  drwi::fsm::RouteWatcherFsm fsm;
  const auto& data = TwoCombinedServicesData();

  SetToSimpleTrackingState(fsm, env, data);
  // Break main router
  env.router.SetThrow();

  fsm.SetPosition(*env.context, data.not_adjustible);
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<RouteRequestState>()->GetName());
  ASSERT_NO_THROW(ProcessRouteFail(fsm, env));
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<FallbackTrackingState>()->GetName());
}

/// Test we able to adjust initial position to route even if this position is
/// much far than max adjust distance
UTEST(worker_fsm, adjust_far_position_on_route_requested) {
  drwm::DriverPosition src_pos(10 * lat, 10 * lon, kTransportType, kAdjusted);
  auto dst_pos = MakeDestination({10 * lat, 20 * lon});

  const auto driver_id = drwm::DriverId(driver_id::DriverDbid("dbid"),
                                        driver_id::DriverUuid("uuid"));

  drw::test_utils::WorkerFsmEnvironment env(driver_id);
  drwi::Config new_config;
  new_config.SetMaxAdjustDistance(100 * geometry::meter);
  new_config.SetEnableAllPointRouting(true);
  env.SetConfig(new_config);

  // Initial state
  drwi::fsm::RouteWatcherFsm fsm;

  // Set position (gps)
  fsm.SetPosition(*env.context, src_pos);
  // Set destination (start-watch)
  fsm.SetDestination(*env.context, dst_pos);

  // Wait route response appear in message queue
  auto deadline = engine::Deadline::FromDuration(std::chrono::seconds(3));
  drwi::InputMessage message = env.message_queue.BlockingPop(deadline);
  const auto& route_message = std::get<drwi::RouteMessage>(message.data);
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<RouteRequestState>()->GetName());

  /// substitute route with some distant route
  auto route = driver_route_watcher::test_utils::MakeTwoPointsRoute(
      {geometry::Position{(10 - 0.001) * lat, 10 * lon},
       dst_pos.GetDestinationPoint()});

  // Received route succesfully, pass it to fsm, should switch to Tracking
  ASSERT_NO_THROW(fsm.SetRoute(*env.context, std::move(route),
                               route_message.request_id,
                               std::move(route_message.request_reason),
                               route_message.first_segment_was_rebuilt));
  ASSERT_EQ(1ul, env.storage_.outputs_updated);

  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<TrackingState>()->GetName());
}

/// check switching unknown_b/known_b destination does not lead to crash
/// unknown_B -> with_B
UTEST(worker_fsm, order_without_B_1) {
  const auto driver_id = drwm::DriverId(driver_id::DriverDbid("dbid"),
                                        driver_id::DriverUuid("uuid"));
  const auto unknown_b = MakeUnknownDestination();
  const auto known_b = MakeDestination({10 * lat, 13 * lon});

  drwm::DriverPosition src_pos(10 * lat, 10 * lon, kTransportType, kAdjusted);
  drwm::DriverPosition pos1(10 * lat, 11 * lon, kTransportType,
                            kAdjusted);  // Move along the route

  drw::test_utils::WorkerFsmEnvironment env(driver_id);

  drwi::Config config;
  config.SetEnableAllPointRouting(true);
  env.SetConfig(config);

  // Initial state
  drwi::fsm::RouteWatcherFsm fsm;
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<WaitDataState>()->GetName());

  fsm.SetDestination(*env.context, unknown_b);
  fsm.SetPosition(*env.context, src_pos);
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<UnknownDestinationState>()->GetName());

  fsm.SetDestination(*env.context, known_b);
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<RouteRequestState>()->GetName());
  ProcessRoute(fsm, env);
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<TrackingState>()->GetName());
  fsm.SetDestination(*env.context, unknown_b);
  ASSERT_EQ(fsm.GetCurrentState()->GetName(),
            fsm.GetStateInstance<UnknownDestinationState>()->GetName());
}
