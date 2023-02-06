#include "storage_synchronizer.hpp"

#include <userver/tracing/span.hpp>
#include <userver/utest/utest.hpp>

namespace {
using driver_route_watcher::models::Destination;
using driver_route_watcher::models::DriverId;
using driver_route_watcher::models::Position;
using driver_route_watcher::models::ServiceId;
using driver_route_watcher::models::TimePoint;
using driver_route_watcher::models::TransportType;
using ::geometry::lat;
using ::geometry::lon;

const auto kPropocessingDriving = "processing:driving";
const auto kProcessingTransporting = "processing:transporting";
const auto service0 =
    driver_route_watcher::models::ServiceId(kPropocessingDriving);
const auto service1 =
    driver_route_watcher::models::ServiceId(kProcessingTransporting);
const auto meta0 = "{\"field\": \"meta0\"}";
const auto meta1 = "{\"field\": \"meta1\"}";
const auto src_pos0 = Position(10 * lat, 10 * lon);
const auto src_pos1 = Position(11 * lat, 11 * lon);

DriverId MakeDriverId(std::string_view uuid) {
  return DriverId(driver_id::DriverDbid("dbid"), driver_id::DriverUuid(uuid));
}

const auto kDefaultPrioritiesSettings = driver_route_watcher::internal::
    WatchListSynchronizer::ServicePrioritiesConfig{
        {kProcessingTransporting, 100},
        {kPropocessingDriving, 90},
        {"", 50},
    };

driver_route_watcher::models::Destination MakeDestination(
    std::vector<Position> points, ServiceId service0, std::string meta0,
    TimePoint now, std::optional<std::string> order_id = std::nullopt,
    TransportType transport_type = TransportType::kCar) {
  return Destination(
      {points.begin(), points.end()}, service0, meta0, now, transport_type,
      driver_route_watcher::models::ToOrderId(order_id), std::nullopt,
      driver_route_watcher::models::Destination::kDefaultEtaMultiplier,
      std::nullopt, std::nullopt,
      driver_route_watcher::models::Destination::kDefaultSourcePosition);
}
}  // namespace

UTEST(watch_list_synchronizer, no_start_stops) {
  using driver_route_watcher::internal::WatchListSynchronizer;
  using driver_route_watcher::models::Destination;
  using driver_route_watcher::models::DriverId;
  using driver_route_watcher::models::Position;
  using ::geometry::lat;
  using ::geometry::lon;
  using LocalWatchedMap = WatchListSynchronizer::LocalWatchedMap;
  using DbWatchedMap = WatchListSynchronizer::DbWatchedMap;

  const auto points = {src_pos0};
  const auto now = utils::datetime::Now();
  auto start = [](DriverId, Destination) { ASSERT_TRUE(false); };
  auto stop = [](DriverId, Destination) { ASSERT_TRUE(false); };
  WatchListSynchronizer synchronizer(start, stop);

  LocalWatchedMap local = {
      {MakeDriverId("uuid0"), MakeDestination(points, service0, meta0, now)},
  };
  DbWatchedMap db = {
      {
          MakeDriverId("uuid0"),
          {
              {service0, MakeDestination(points, service0, meta0, now)},
          },
      },
  };
  tracing::Span ts("test");
  auto scope_time = ts.CreateScopeTime();
  synchronizer.Synchronize(std::move(local), std::move(db),
                           kDefaultPrioritiesSettings, scope_time);
}

UTEST(watch_list_synchronizer, start_watch_simple) {
  using driver_route_watcher::internal::WatchListSynchronizer;
  using driver_route_watcher::models::Destination;
  using driver_route_watcher::models::DriverId;
  using driver_route_watcher::models::Position;
  using ::geometry::lat;
  using ::geometry::lon;
  using LocalWatchedMap = WatchListSynchronizer::LocalWatchedMap;
  using DbWatchedMap = WatchListSynchronizer::DbWatchedMap;

  size_t start_called = 0;
  const auto points = {src_pos0};
  const auto now = utils::datetime::Now();
  const auto driver0 = MakeDriverId("uuid0");
  auto stop = [](DriverId, Destination) { ASSERT_TRUE(false); };
  auto start = [&start_called, &driver0](DriverId driver_id,
                                         Destination destination) {
    ++start_called;
    ASSERT_EQ(driver_id, driver0);
    ASSERT_EQ(destination.metainfo, meta0);
    ASSERT_EQ(destination.service_id, service0);
  };
  WatchListSynchronizer synchronizer(start, stop);

  LocalWatchedMap local = {};
  DbWatchedMap db = {
      {
          driver0,
          {
              {service0, MakeDestination(points, service0, meta0, now)},
          },
      },
  };
  tracing::Span ts("test");
  auto scope_time = ts.CreateScopeTime();
  synchronizer.Synchronize(std::move(local), std::move(db),
                           kDefaultPrioritiesSettings, scope_time);

  ASSERT_EQ(1ul, start_called);
}

UTEST(watch_list_synchronizer, stop_watch_simple) {
  using driver_route_watcher::internal::WatchListSynchronizer;
  using driver_route_watcher::models::Destination;
  using driver_route_watcher::models::DriverId;
  using driver_route_watcher::models::Position;
  using ::geometry::lat;
  using ::geometry::lon;
  using LocalWatchedMap = WatchListSynchronizer::LocalWatchedMap;
  using DbWatchedMap = WatchListSynchronizer::DbWatchedMap;

  size_t stop_called = 0;
  const auto points = {src_pos0};
  const auto now = utils::datetime::Now();
  const auto driver0 = MakeDriverId("uuid0");
  auto start = [](DriverId, Destination) { ASSERT_TRUE(false); };
  auto stop = [&stop_called, &driver0](DriverId driver_id,
                                       Destination destination) {
    ++stop_called;
    ASSERT_EQ(driver_id, driver0);
    ASSERT_EQ(destination.metainfo, meta0);
    ASSERT_EQ(destination.service_id, service0);
  };
  WatchListSynchronizer synchronizer(start, stop);

  LocalWatchedMap local = {
      {driver0, MakeDestination(points, service0, meta0, now)},
  };
  DbWatchedMap db = {};
  tracing::Span ts("test");
  auto scope_time = ts.CreateScopeTime();
  synchronizer.Synchronize(std::move(local), std::move(db),
                           kDefaultPrioritiesSettings, scope_time);

  ASSERT_EQ(1ul, stop_called);
}

UTEST(watch_list_synchronizer, start_watch_higher_priority) {
  namespace drwi = driver_route_watcher::internal;
  using driver_route_watcher::internal::WatchListSynchronizer;
  using driver_route_watcher::models::Destination;
  using driver_route_watcher::models::DriverId;
  using driver_route_watcher::models::Position;
  using ::geometry::lat;
  using ::geometry::lon;
  using LocalWatchedMap = WatchListSynchronizer::LocalWatchedMap;
  using DbWatchedMap = WatchListSynchronizer::DbWatchedMap;

  tracing::Span ts("test");
  auto scope_time = ts.CreateScopeTime();

  size_t start_called = 0;
  const auto points0 = {src_pos0};
  const auto points1 = {src_pos1};
  const auto now = utils::datetime::Now();
  const auto driver0 = MakeDriverId("uuid0");
  auto stop = [](DriverId, Destination) { ASSERT_TRUE(false); };
  auto start = [&start_called, &driver0](DriverId driver_id,
                                         Destination destination) {
    ++start_called;
    ASSERT_EQ(driver_id, driver0);
    ASSERT_EQ(destination.metainfo, meta1);
    ASSERT_EQ(destination.service_id, service1);
    ASSERT_TRUE(
        drwi::IsEqual(destination.ExpressDestinationAsPosition(), src_pos1));
  };
  WatchListSynchronizer synchronizer(start, stop);

  /// Start watch destination from highest priority from db
  {
    start_called = 0;
    LocalWatchedMap local = {};
    DbWatchedMap db = {
        {
            driver0,
            {
                {service0, MakeDestination(points0, service0, meta0, now)},
                {service1, MakeDestination(points1, service1, meta1, now)},
            },
        },
    };
    synchronizer.Synchronize(std::move(local), std::move(db),
                             kDefaultPrioritiesSettings, scope_time);
    ASSERT_EQ(1ul, start_called);
  }

  /// Start watch destination from highest priority from db
  /// Override current destination by highest priority from db
  {
    start_called = 0;
    LocalWatchedMap local = {
        {driver0, MakeDestination(points0, service0, meta0, now)},
    };
    DbWatchedMap db = {
        {
            driver0,
            {
                {service0, MakeDestination(points0, service0, meta0, now)},
                {service1, MakeDestination(points1, service1, meta1, now)},
            },
        },
    };
    synchronizer.Synchronize(std::move(local), std::move(db),
                             kDefaultPrioritiesSettings, scope_time);
    ASSERT_EQ(1ul, start_called);
  }
}

UTEST(watch_list_synchronizer, watch_lower_priority_after_higher_gone) {
  namespace drwi = driver_route_watcher::internal;
  using driver_route_watcher::internal::WatchListSynchronizer;
  using driver_route_watcher::models::Destination;
  using driver_route_watcher::models::DriverId;
  using driver_route_watcher::models::Position;
  using ::geometry::lat;
  using ::geometry::lon;
  using LocalWatchedMap = WatchListSynchronizer::LocalWatchedMap;
  using DbWatchedMap = WatchListSynchronizer::DbWatchedMap;

  size_t start_called = 0;
  const auto points0 = {src_pos0};
  const auto points1 = {src_pos1};
  const auto now = utils::datetime::Now();
  const auto driver0 = MakeDriverId("uuid0");
  auto stop = [](DriverId, Destination) { ASSERT_TRUE(false); };
  auto start = [&start_called, &driver0](DriverId driver_id,
                                         Destination destination) {
    ++start_called;
    ASSERT_EQ(driver_id, driver0);
    ASSERT_EQ(destination.metainfo, meta0);
    ASSERT_EQ(destination.service_id, service0);
    ASSERT_TRUE(
        drwi::IsEqual(destination.ExpressDestinationAsPosition(), src_pos0));
  };
  WatchListSynchronizer synchronizer(start, stop);

  // Watch high priority now
  LocalWatchedMap local = {
      {driver0, MakeDestination(points1, service1, meta1, now)},
  };
  DbWatchedMap db = {
      {
          driver0,
          {
              // No more hight priority in db
              // So watch what we have
              {service0, MakeDestination(points0, service0, meta0, now)},
          },
      },
  };
  tracing::Span ts("test");
  auto scope_time = ts.CreateScopeTime();
  synchronizer.Synchronize(std::move(local), std::move(db),
                           kDefaultPrioritiesSettings, scope_time);

  ASSERT_EQ(1ul, start_called);
}

/// Not listed in config services should be processed by lexicographical order
UTEST(watch_list_synchronizer, not_listed_in_config) {
  namespace drwi = driver_route_watcher::internal;
  using driver_route_watcher::internal::WatchListSynchronizer;
  using driver_route_watcher::models::Destination;
  using driver_route_watcher::models::DriverId;
  using driver_route_watcher::models::Position;
  using ::geometry::lat;
  using ::geometry::lon;
  using LocalWatchedMap = WatchListSynchronizer::LocalWatchedMap;
  using DbWatchedMap = WatchListSynchronizer::DbWatchedMap;

  size_t start_called = 0;
  const auto points0 = {src_pos0};
  const auto points1 = {src_pos1};
  const auto now = utils::datetime::Now();
  const auto kEmptyConfig = driver_route_watcher::internal::
      WatchListSynchronizer::ServicePrioritiesConfig();
  const auto driver0 = MakeDriverId("uuid0");
  auto stop = [](DriverId, Destination) { ASSERT_TRUE(false); };
  auto start = [&start_called, &driver0](DriverId driver_id,
                                         Destination destination) {
    ++start_called;
    ASSERT_EQ(driver_id, driver0);
    ASSERT_EQ(destination.metainfo, meta0);
    ASSERT_EQ(destination.service_id, service0);
    ASSERT_TRUE(
        drwi::IsEqual(destination.ExpressDestinationAsPosition(), src_pos0));
  };
  WatchListSynchronizer synchronizer(start, stop);

  LocalWatchedMap local = {};
  DbWatchedMap db = {
      {
          driver0,
          {
              {service1, MakeDestination(points1, service1, meta1, now)},
              /// processing:driving must be choosen
              /// couse 'd' prior 't'
              {service0, MakeDestination(points0, service0, meta0, now)},
          },
      },
  };
  tracing::Span ts("test");
  auto scope_time = ts.CreateScopeTime();
  synchronizer.Synchronize(std::move(local), std::move(db), kEmptyConfig,
                           scope_time);

  ASSERT_EQ(1ul, start_called);
}

TEST(get_highest_priority, no_config) {
  auto destinations = driver_route_watcher::models::DestinationsByService{
      {ServiceId("service_c"), {}},
      {ServiceId("service_a"), {}},  // lexicographically first
      {ServiceId("service_b"), {}},
  };
  auto priorities = std::unordered_map<std::string, double>{};
  auto ret = driver_route_watcher::internal::GetServiceWithHighestPriority(
      destinations, priorities);
  ASSERT_EQ(ret->first, ServiceId("service_a"));
}

TEST(get_highest_priority, config) {
  auto destinations = driver_route_watcher::models::DestinationsByService{
      {ServiceId("service_a"), {}},
      {ServiceId("service_c"), {}},
      {ServiceId("service_b"), {}},
  };
  auto priorities = std::unordered_map<std::string, double>{
      {"service_b", 10},
      // Max priority
      {"service_c", 11},
  };
  auto ret = driver_route_watcher::internal::GetServiceWithHighestPriority(
      destinations, priorities);
  ASSERT_EQ(ret->first, ServiceId("service_c"));
}
