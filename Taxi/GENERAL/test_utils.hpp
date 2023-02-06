#pragma once
#include "internal/worker/worker.hpp"
#include "internal/worker/worker_dependencies.hpp"
#include "internal/worker/worker_fsm/worker_fsm_data.hpp"
#include "statistics/route_watcher_statistics.hpp"

#include <clients/routing/exceptions.hpp>
#include <clients/routing/test/router_mock.hpp>

#include <optional>

#include <userver/rcu/rcu.hpp>
#include <userver/utils/assert.hpp>

namespace driver_route_watcher::test_utils {
const int kRouteTime = 40;
const int kRouteDistance = 1000;

class TestStorage final : public driver_route_watcher::internal::IStorage {
 public:
  using Route = driver_route_watcher::models::Route;
  using TrackingData = driver_route_watcher::models::TrackingData;

  bool SetFsmRestoreData(const DriverId& driver_id,
                         const models::TrackingData& tracking_data,
                         const std::optional<models::Route>& route,
                         const models::DriverPosition& driver_position,
                         models::FsmStateType current_state,
                         models::TimePoint current_state_start_time) override {
    if (route) SetRoute(driver_id, *route, utils::datetime::Now());
    output.insert_or_assign(driver_id, tracking_data);
    ++outputs_updated;

    if (restore_data.find(driver_id) == restore_data.end() || route) {
      restore_data.insert_or_assign(
          driver_id,
          models::FsmRestoreData{route, current_state, current_state_start_time,
                                 driver_position, std::nullopt});
      return true;
    }
    restore_data[driver_id].current_state = current_state;
    restore_data[driver_id].current_state_start_time = current_state_start_time;
    restore_data[driver_id].driver_position = driver_position;
    return true;
  }

  std::optional<models::FsmRestoreData> GetFsmRestoreData(
      const DriverId& driver_id) override {
    const auto it = restore_data.find(driver_id);
    if (it == restore_data.end()) {
      return std::nullopt;
    }
    return it->second;
  }

  std::optional<models::Route> GetMainRoute(
      const DriverId& driver_id) override {
    auto it = routes.find(driver_id);
    if (it == routes.end()) {
      return std::nullopt;
    }
    return it->second;
  }

  bool SetRoute(const models::RouteId& route_id, const Route& route,
                const models::TimePoint&) override {
    full_routes[route_id] = route;
    return true;
  }

  void DeleteRoute(const models::RouteId& route_id) override {
    full_routes.erase(route_id);
  }

  bool ClearOutput(const DriverId& driver_id) override {
    auto ret = output.erase(driver_id);
    restore_data.erase(driver_id);
    routes.erase(driver_id);
    ++outputs_cleared;
    return ret != 0;
  }

  bool SetRoute(const DriverId& driver_id, const Route& route,
                const driver_route_watcher::models::TimePoint&) override {
    routes[driver_id] = route;
    ++routes_stored;
    return true;
  }

  bool SetWatch(const DriverId&, Destination) override { return true; }
  bool SetWatchWithOrderIds(const DriverId&, Destination) override {
    return true;
  }

  bool ResetWatch(const DriverId&, const DestinationPosition&,
                  const ServiceId&) override {
    return true;
  }
  bool ResetWatch(const DriverId&, const std::vector<DestinationPosition>&,
                  const ServiceId&) override {
    return true;
  }
  bool ResetWatchNoCheckPoint(const DriverId&, const ServiceId&) override {
    return true;
  }
  bool ResetWatchByOrderId(const DriverId&, const ServiceId&,
                           const OrderId&) override {
    return true;
  }
  bool ResetWatchByOrderId(const DriverId&, const ServiceId&,
                           const std::unordered_set<OrderId>&) override {
    return true;
  }
  void ResetWatchIgnoreResult(const DriverId&, const DestinationPosition&,
                              const ServiceId&) override{};
  Destinations GetWatched() override { return {}; }
  void SetForceLogFlag(const DriverId&) override {}

  size_t routes_stored = 0;
  size_t outputs_updated = 0;
  size_t outputs_cleared = 0;
  std::unordered_map<DriverId, TrackingData> output;
  std::unordered_map<DriverId, Route> routes;
  std::unordered_map<models::RouteId, Route> full_routes;
  std::unordered_map<DriverId, models::FsmRestoreData> restore_data;
};

class TestExperiments : public internal::ExperimentsBase {
 public:
  std::optional<Values> GetExperimentsValues(
      const models::DriverId&,
      const std::optional<models::ZoneId>&) const override {
    ++request_count;
    return result_;
  }

  void SetResult(std::optional<Values> result) { result_ = std::move(result); }

  size_t GetRequestCount() const { return request_count; }

 private:
  std::optional<Values> result_ = std::nullopt;
  mutable size_t request_count = 0;
};

// Make Route from points
inline driver_route_watcher::models::Route MakeTwoPointsRoute(
    const std::vector<::geometry::Position>& path) {
  UINVARIANT(path.size() == 2ul, "path must have 2 points");
  const auto& src = path.front();
  const auto& dst = path.back();

  driver_route_watcher::models::Route ret;
  ret.path.push_back(clients::routing::RoutePoint{src});

  clients::routing::RoutePoint dst_point(dst);
  dst_point.distance_since_ride_start = kRouteDistance * ::geometry::meter;
  dst_point.time_since_ride_start = std::chrono::seconds(kRouteTime);

  ret.path.push_back(dst_point);
  ret.info = clients::routing::RouteInfo(kRouteTime, kRouteDistance);
  ret.legs = {{0}};

  return ret;
}

class TestRouter {
 public:
  TestRouter(clients::routing::RouterType transport_type =
                 clients::routing::RouterType::kCar)
      : router_mock{
            std::make_unique<::testing::NiceMock<clients::routing::RouterMock>>(
                routing_base::ToRouterVehicleType(transport_type))} {
    using ::testing::Return;
    router_mock->EnableDefaults();
    router_mock->SetDefaultMakeNPointsRoute();
  }

  driver_route_watcher::models::Route operator()(
      const std::vector<::geometry::Position>& path,
      std::optional<::geometry::Azimuth> source_direction,
      const clients::routing::RouterSettings& router_settings = {}) const {
    return router_mock->FetchRoutePath(path, source_direction, router_settings,
                                       {});
  }

  void SetThrow(bool should_throw = true) {
    if (should_throw) {
      router_mock->SetDefaultFetchRoutePathAndInfo(
          [](const auto&, const auto&, const auto&,
             const auto&) -> clients::routing::RoutePath {
            throw clients::routing::BaseError("mock client error");
            return {};
          });
    } else {
      router_mock->SetDefaultMakeTwoPointsRoute();
    }
  }
  /// Make router return   invalid route with one point
  void SetOnePoint(bool one_point = true) {
    if (one_point) {
      router_mock->SetDefaultMakeOnePointRoute();
    } else {
      router_mock->SetDefaultMakeTwoPointsRoute();
    }
  }

  std::unique_ptr<::testing::NiceMock<clients::routing::RouterMock>>
      router_mock;

 private:
};

class TestStatistics {
 public:
  driver_route_watcher::statistics::RouteWatcherStatistics& GetStatistics() {
    return storage_.GetCurrentCounter();
  }

  driver_route_watcher::statistics::LocalStorageStats& GetLocalStorageStats() {
    return local_storage_stats_;
  }

 private:
  driver_route_watcher::statistics::RouteWatcherStatisticsStorage storage_;
  driver_route_watcher::statistics::LocalStorageStats local_storage_stats_;
};

class TestMasterSlave {
 public:
  std::optional<size_t> IsMaster() const { return is_master_; }
  void SetIsMaster(std::optional<size_t> is_master) { is_master_ = is_master; }

 private:
  std::optional<size_t> is_master_;
};

/// TODO: Move to test utils
struct Env {
  using Deps = driver_route_watcher::internal::WorkerDependencies;
  using DriverId = driver_route_watcher::models::DriverId;
  using RouteId = driver_route_watcher::models::RouteId;
  using LoggerFunc = driver_route_watcher::models::LoggerFunc;
  using PublishEtaFunc = driver_route_watcher::models::PublishEtaFunc;
  using PublishAllPointTimeleftsFunc =
      driver_route_watcher::models::PublishAllPointTimeleftsFunc;
  using PublishFullGeometryPointsFunc =
      driver_route_watcher::models::PublishFullGeometryPointsFunc;
  using PublishRoutePredictedPointsFunc =
      driver_route_watcher::models::PublishRoutePredictedPointsFunc;
  using RouterFunc = driver_route_watcher::models::RouterFunc;
  using Stats = driver_route_watcher::statistics::RouteWatcherStatistics;
  using LocalStorageStats = driver_route_watcher::statistics::LocalStorageStats;
  using StatsFunc = driver_route_watcher::models::StatisticsFunc;
  using LocalStorageStatsFunc =
      driver_route_watcher::models::LocalStorageStatsFunc;
  using MasterSlaveFunc = driver_route_watcher::models::MasterSlaveFunc;
  using IStorage = driver_route_watcher::internal::IStorage;
  using Config = driver_route_watcher::internal::Config;
  using GetDriverPositionFromCacheFunc =
      driver_route_watcher::models::GetDriverPositionFromCacheFunc;
  using DriverPosition = driver_route_watcher::models::DriverPosition;
  using PositionsCache = std::unordered_map<DriverId, DriverPosition>;

  Env()
      : config_(std::make_shared<rcu::Variable<Config>>()),
        deps(std::make_shared<Deps>(
            MakeRouterFunc(), MakeFallbackRouterFunc(), MakeMasterSlaveFunc(),
            storage_, MakePublishAllPointTimeleftsFunc(),
            MakePublishFullGeometryPointsFunc(),
            MakePublishRoutePredictedPointsFunc(), MakeLoggerFunc(),
            MakeStatsFunc(), MakeLocalStorageStatsFunc(),
            MakeGetDriverPositionFromCacheFunc(), config_,
            std::make_unique<TestExperiments>())) {}

  std::shared_ptr<rcu::Variable<Config>> config_;
  PositionsCache positions_cache_;
  std::shared_ptr<Deps> deps;
  driver_route_watcher::test_utils::TestRouter router;
  driver_route_watcher::test_utils::TestRouter pedestrian_router;
  driver_route_watcher::test_utils::TestRouter fallback_router;
  driver_route_watcher::test_utils::TestRouter pedestrian_fallback_router;
  driver_route_watcher::test_utils::TestStatistics statistics_storage_;
  driver_route_watcher::test_utils::TestStorage storage_;
  TestMasterSlave master_slave_;

 private:
  MasterSlaveFunc MakeMasterSlaveFunc() {
    return [this] { return master_slave_.IsMaster(); };
  }

  RouterFunc MakeRouterFunc() {
    return [this](const auto& path, auto source_direction, auto transport_type,
                  auto use_toll_roads, auto zone_id, auto driver_id,
                  auto order_id) {
      std::ignore = zone_id;
      std::ignore = driver_id;
      std::ignore = order_id;
      if (transport_type ==
          driver_route_watcher::models::TransportType::kPedestrian)
        return pedestrian_router(path, source_direction);

      clients::routing::RouterSettings router_settings;
      if (transport_type == driver_route_watcher::models::TransportType::kCar) {
        router_settings.tolls =
            (use_toll_roads ? routing_base::RouterTolls::kTolls
                            : routing_base::RouterTolls::kNoTolls);
      }

      return router(path, source_direction, router_settings);
    };
  }

  RouterFunc MakeFallbackRouterFunc() {
    return [this](const auto& path, auto source_direction, auto transport_type,
                  auto use_toll_roads, auto zone_id, auto driver_id,
                  auto order_id) {
      std::ignore = use_toll_roads;
      std::ignore = zone_id;
      std::ignore = driver_id;
      std::ignore = order_id;
      if (transport_type ==
          driver_route_watcher::models::TransportType::kPedestrian)
        return pedestrian_fallback_router(path, source_direction);
      return fallback_router(path, source_direction);
    };
  }

  StatsFunc MakeStatsFunc() {
    return [this]() -> Stats& { return statistics_storage_.GetStatistics(); };
  }

  LocalStorageStatsFunc MakeLocalStorageStatsFunc() {
    return [this]() -> LocalStorageStats& {
      return statistics_storage_.GetLocalStorageStats();
    };
  }

  LoggerFunc MakeLoggerFunc() {
    return
        [](const DriverId&, const std::string&, const std::string&,
           const std::string&,
           const std::optional<driver_route_watcher::models::DriverPosition>&,
           const std::optional<driver_route_watcher::models::Destination>&,
           const std::optional<driver_route_watcher::models::TrackingData>&,
           const std::optional<driver_route_watcher::models::Route>&,
           const models::LogNotes&, bool) {};
  }

  PublishAllPointTimeleftsFunc MakePublishAllPointTimeleftsFunc() {
    return [](const DriverId&,
              const driver_route_watcher::models::TrackingData&) {};
  }
  PublishFullGeometryPointsFunc MakePublishFullGeometryPointsFunc() {
    return [](const DriverId&, const models::TrackingData&,
              const std::optional<models::Route>&,
              const std::optional<models::PublishedFullGeometryPoint>&) {
      return models::PublishedFullGeometryPoint{};
    };
  }
  PublishRoutePredictedPointsFunc MakePublishRoutePredictedPointsFunc() {
    return
        [](const DriverId&, const models::TrackingData&,
           const std::optional<models::Route>&) { return models::LogNotes{}; };
  }

  GetDriverPositionFromCacheFunc MakeGetDriverPositionFromCacheFunc() {
    return [this](const DriverId& driver_id) -> std::optional<DriverPosition> {
      auto it = positions_cache_.find(driver_id);
      if (it == positions_cache_.end()) {
        return std::nullopt;
      }
      return it->second;
    };
  }
};

struct WorkerFsmEnvironment {
  using DriverId = driver_route_watcher::models::DriverId;
  using RouteId = driver_route_watcher::models::RouteId;
  using LoggerFunc = driver_route_watcher::models::LoggerFunc;
  using PublishEtaFunc = driver_route_watcher::models::PublishEtaFunc;
  using PublishAllPointTimeleftsFunc =
      driver_route_watcher::models::PublishAllPointTimeleftsFunc;
  using PublishFullGeometryPointsFunc =
      driver_route_watcher::models::PublishFullGeometryPointsFunc;
  using PublishRoutePredictedPointsFunc =
      driver_route_watcher::models::PublishRoutePredictedPointsFunc;
  using WorkerWatchList = driver_route_watcher::models::WorkerWatchList;
  using WorkerFsmData = driver_route_watcher::internal::fsm::WorkerFsmData;
  using RouterFunc = driver_route_watcher::models::RouterFunc;
  using Stats = driver_route_watcher::statistics::RouteWatcherStatistics;
  using LocalStorageStats = driver_route_watcher::statistics::LocalStorageStats;
  using StatsFunc = driver_route_watcher::models::StatisticsFunc;
  using LocalStorageStatsFunc =
      driver_route_watcher::models::LocalStorageStatsFunc;
  using MasterSlaveFunc = driver_route_watcher::models::MasterSlaveFunc;
  using IStorage = driver_route_watcher::internal::IStorage;
  using GetDriverPositionFromCacheFunc =
      driver_route_watcher::models::GetDriverPositionFromCacheFunc;

  using Config = driver_route_watcher::internal::Config;
  using FsmContext = driver_route_watcher::internal::fsm::FsmContext;
  using InputMessagesQueue = driver_route_watcher::internal::InputMessagesQueue;
  using WorkerDeps = driver_route_watcher::internal::WorkerDependencies;

  WorkerFsmEnvironment(DriverId driver_id, bool master = true)
      : data(std::move(driver_id)),
        config(std::make_shared<rcu::Variable<Config>>()),
        deps(master ? MakeDeps() : MakeSlaveDeps()),
        context(std::make_shared<FsmContext>(
            data, deps->GetMainRouter(), deps->GetFallbackRouter(),
            message_queue, output, deps->GetMasterSlaveFunc(),
            deps->GetStorage(), deps->GetPublishAllPointTimeleftsFunc(),
            deps->GetPublishFullGeometryPointsFunc(),
            deps->GetPublishPredictedPointsFunc(), deps->GetLogger(),
            deps->GetStats(), deps->GetConfig(), deps->GetExperiments())) {}

  void SetConfig(const driver_route_watcher::internal::Config& config) {
    this->config->Assign(config);
    context = std::make_shared<FsmContext>(
        data, deps->GetMainRouter(), deps->GetFallbackRouter(), message_queue,
        output, deps->GetMasterSlaveFunc(), deps->GetStorage(),
        deps->GetPublishAllPointTimeleftsFunc(),
        deps->GetPublishFullGeometryPointsFunc(),
        deps->GetPublishPredictedPointsFunc(), deps->GetLogger(),
        deps->GetStats(), deps->GetConfig(), deps->GetExperiments());
  }

  TestRouter router;
  TestRouter pedestrian_router;
  TestRouter fallback_router;
  TestRouter pedestrian_fallback_router;
  TestStatistics statistics_storage_;
  TestStorage storage_;

  InputMessagesQueue message_queue;
  WorkerWatchList output;
  WorkerFsmData data;
  std::shared_ptr<rcu::Variable<Config>> config;
  std::shared_ptr<WorkerDeps> deps;
  std::shared_ptr<FsmContext> context;

 private:
  std::shared_ptr<WorkerDeps> MakeDeps() {
    return std::make_shared<WorkerDeps>(
        MakeRouterFunc(), MakeFallbackRouterFunc(), MakeMasterSlaveFunc(),
        storage_, MakePublishAllPointTimeleftsFunc(),
        MakePublishFullGeometryPointsFunc(),
        MakePublishRoutePredictedPointsFunc(), MakeLoggerFunc(),
        MakeStatsFunc(), MakeLocalStorageStatsFunc(),
        MakeGetDriverPositionFromCacheFunc(), config,
        std::make_unique<TestExperiments>());
  }
  std::shared_ptr<WorkerDeps> MakeSlaveDeps() {
    return std::make_shared<WorkerDeps>(
        MakeRouterFunc(), MakeFallbackRouterFunc(), MakeSlaveFunc(), storage_,
        MakePublishAllPointTimeleftsFunc(), MakePublishFullGeometryPointsFunc(),
        MakePublishRoutePredictedPointsFunc(), MakeLoggerFunc(),
        MakeStatsFunc(), MakeLocalStorageStatsFunc(),
        MakeGetDriverPositionFromCacheFunc(), config,
        std::make_unique<TestExperiments>());
  }

  RouterFunc MakeExceptionRouterFunc() {
    return
        [](const auto&, auto, auto, auto, auto, auto, auto) -> models::Route {
          throw std::logic_error("Router should'not requested");
        };
  }

  RouterFunc MakeRouterFunc() {
    return [this](const auto& path, auto direction, auto transport_type,
                  auto use_toll_roads, auto, auto, auto) {
      if (transport_type ==
          driver_route_watcher::models::TransportType::kPedestrian)
        return pedestrian_router(path, direction);

      clients::routing::RouterSettings router_settings;
      if (transport_type == driver_route_watcher::models::TransportType::kCar) {
        router_settings.tolls =
            (use_toll_roads ? routing_base::RouterTolls::kTolls
                            : routing_base::RouterTolls::kNoTolls);
      }

      return router(path, direction);
    };
  }

  RouterFunc MakeFallbackRouterFunc() {
    return [this](const auto& path, auto direction, auto transport_type,
                  auto use_toll_roads, auto, auto, auto) {
      std::ignore = use_toll_roads;
      if (transport_type ==
          driver_route_watcher::models::TransportType::kPedestrian)
        return pedestrian_fallback_router(path, direction);
      return fallback_router(path, direction);
    };
  }

  StatsFunc MakeStatsFunc() {
    return [this]() -> Stats& { return statistics_storage_.GetStatistics(); };
  }

  LocalStorageStatsFunc MakeLocalStorageStatsFunc() {
    return [this]() -> LocalStorageStats& {
      return statistics_storage_.GetLocalStorageStats();
    };
  }

  LoggerFunc MakeLoggerFunc() {
    return
        [](const DriverId&, const std::string&, const std::string&,
           const std::string&,
           const std::optional<driver_route_watcher::models::DriverPosition>&,
           const std::optional<driver_route_watcher::models::Destination>&,
           const std::optional<driver_route_watcher::models::TrackingData>&,
           const std::optional<driver_route_watcher::models::Route>&,
           const models::LogNotes&, bool) {};
  }

  MasterSlaveFunc MakeMasterSlaveFunc() {
    return [] { return std::optional<size_t>{1}; };
  }
  MasterSlaveFunc MakeSlaveFunc() {
    return []() -> std::optional<size_t> { return std::nullopt; };
  }
  PublishAllPointTimeleftsFunc MakePublishAllPointTimeleftsFunc() {
    return [](const DriverId&,
              const driver_route_watcher::models::TrackingData&) {};
  }
  PublishFullGeometryPointsFunc MakePublishFullGeometryPointsFunc() {
    return [](const DriverId&, const models::TrackingData&,
              const std::optional<models::Route>&,
              const std::optional<models::PublishedFullGeometryPoint>&) {
      return models::PublishedFullGeometryPoint{};
    };
  }
  PublishRoutePredictedPointsFunc MakePublishRoutePredictedPointsFunc() {
    return
        [](const DriverId&, const models::TrackingData&,
           const std::optional<models::Route>&) { return models::LogNotes{}; };
  }

  GetDriverPositionFromCacheFunc MakeGetDriverPositionFromCacheFunc() {
    return [](const DriverId&) { return std::nullopt; };
  }
};

inline driver_route_watcher::models::Destination MakeDestination(
    const driver_route_watcher::models::Position& position,
    const driver_route_watcher::models::ServiceId& service_id,
    const driver_route_watcher::models::TimePoint watched_since =
        utils::datetime::Now(),
    const std::string& meta_info = "some-meta-info",
    const std::optional<std::string>& order_id = std::nullopt) {
  std::vector<driver_route_watcher::models::DestinationPoint> points;
  if (!internal::IsEmpty(position)) {
    points.push_back(models::DestinationPoint(position));
  }
  const auto transport_type = driver_route_watcher::models::TransportType::kCar;
  return {points,
          service_id,
          meta_info,
          watched_since,
          transport_type,
          models::ToOrderId(order_id),
          std::nullopt,
          models::Destination::kDefaultEtaMultiplier,
          std::nullopt,
          std::nullopt,
          models::Destination::kDefaultSourcePosition};
}

inline driver_route_watcher::models::Destination MakeDestination(
    const driver_route_watcher::models::Position& position,
    const driver_route_watcher::models::TimePoint watched_since =
        utils::datetime::Now(),
    const std::string& service_id = "some-service-id",
    const std::string& meta_info = "some-meta-info",
    const std::optional<std::string>& order_id = std::nullopt) {
  std::vector<driver_route_watcher::models::DestinationPoint> points;
  if (!internal::IsEmpty(position)) {
    points.push_back(models::DestinationPoint(position));
  }
  const auto transport_type = driver_route_watcher::models::TransportType::kCar;
  return {points,
          driver_route_watcher::models::ServiceId(service_id),
          meta_info,
          watched_since,
          transport_type,
          models::ToOrderId(order_id),
          std::nullopt,
          models::Destination::kDefaultEtaMultiplier,
          std::nullopt,
          std::nullopt,
          models::Destination::kDefaultSourcePosition};
}

inline std::vector<driver_route_watcher::models::TrackedDestinationPoint>
MakeTrackedDestinationPoint(
    const driver_route_watcher::models::Position& position,
    const std::string& service_id = "some-service-id",
    const std::string& meta_info = "some-meta-info",
    const std::optional<std::string>& order_id = std::nullopt) {
  driver_route_watcher::models::ServiceId typed_service_id{service_id};
  std::optional<driver_route_watcher::models::OrderId> typed_order_id =
      order_id
          ? std::make_optional(driver_route_watcher::models::OrderId{*order_id})
          : std::nullopt;

  if (!position.IsFinite()) {
    return {models::TrackedDestinationPoint::CreateUknownPoint(
        typed_service_id, false, typed_order_id, 0.0, false, std::nullopt,
        std::nullopt, meta_info)};
  }
  driver_route_watcher::models::DestinationPoint point;
  point.position = position;
  point.order_id = typed_order_id;
  return {driver_route_watcher::models::TrackedDestinationPoint(
      std::move(point), typed_service_id, false, typed_order_id, 0.0, false,
      std::nullopt, std::nullopt, meta_info)};
}

inline driver_route_watcher::models::Destination MakeUnknownDestination(
    const std::string& service_id = "some-service-id",
    const driver_route_watcher::models::TimePoint watched_since =
        utils::datetime::Now(),
    const std::string& meta_info = "some-meta-info",
    const std::optional<std::string>& order_id = std::nullopt) {
  const auto transport_type = driver_route_watcher::models::TransportType::kCar;
  return {
      {},
      driver_route_watcher::models::ServiceId(service_id),
      meta_info,
      watched_since,
      transport_type,
      models::ToOrderId(order_id),
      std::nullopt,
      models::Destination::kDefaultEtaMultiplier,
      std::nullopt,
      std::nullopt,
      models::Destination::kDefaultSourcePosition,
  };
}

class TestWorkerViewer {
 public:
  using Worker = ::driver_route_watcher::internal::Worker;
  using RouteStorage = ::driver_route_watcher::internal::RouteStorage;

  TestWorkerViewer(Worker& worker) : worker_(worker) {}
  const RouteStorage& GetLocalStorage() const { return worker_.storage_; }
  RouteStorage& GetLocalStorage() { return worker_.storage_; }

 private:
  Worker& worker_;
};

}  // namespace driver_route_watcher::test_utils
