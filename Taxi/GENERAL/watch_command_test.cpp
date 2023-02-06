#include <gtest/gtest.h>

#include <internal/unittest_utils/test_utils.hpp>
#include "watch_command.hpp"

using driver_route_watcher::test_utils::MakeDestination;

TEST(fbs_watch_command, base) {
  using driver_route_watcher::models::Destination;
  using driver_route_watcher::models::DriverId;
  using driver_route_watcher::models::OrderId;
  using driver_route_watcher::models::WatchCommand;
  using ::geometry::lat;
  using ::geometry::lon;
  using ::geometry::Position;

  const auto now = utils::datetime::Now();
  const auto driver_id = DriverId(driver_id::DriverDbidView("aaaa"),
                                  driver_id::DriverUuidView("bbbb"));
  auto destination = MakeDestination(Position{11 * lat, 22 * lon}, now,
                                     "super-service", "very-usefull-meta");
  destination.eta_multiplier = 0.5;

  WatchCommand orig;
  orig.destination = destination;
  orig.driver_id = driver_id;
  orig.type = WatchCommand::Type::kStart;
  orig.orders = {OrderId("order1"), OrderId("order2"), OrderId("order3")};

  const auto fbs = driver_route_watcher::internal::ToFlatbuffers(orig);
  const auto entry = driver_route_watcher::internal::ToWatchCommand(fbs);
  ASSERT_TRUE(::geometry::AreClosePositions(
      orig.destination.ExpressDestinationAsPosition(),
      entry.destination.ExpressDestinationAsPosition()));
  ASSERT_EQ(orig.destination.service_id, entry.destination.service_id);
  ASSERT_EQ(orig.destination.metainfo, entry.destination.metainfo);
  ASSERT_EQ(orig.destination.order_id, entry.destination.order_id);
  ASSERT_EQ(orig.destination.eta_multiplier, entry.destination.eta_multiplier);
  ASSERT_LE(orig.destination.timestamp - entry.destination.timestamp,
            std::chrono::seconds(1));
  ASSERT_EQ(orig.driver_id, entry.driver_id);
  ASSERT_EQ(orig.orders, entry.orders);

  // check toll roads
  ASSERT_FALSE(*entry.destination.toll_roads);
}

TEST(fbs_watch_command, toll_roads_true) {
  using driver_route_watcher::models::Destination;
  using driver_route_watcher::models::DriverId;
  using driver_route_watcher::models::OrderId;
  using driver_route_watcher::models::WatchCommand;
  using ::geometry::lat;
  using ::geometry::lon;
  using ::geometry::Position;

  const auto now = utils::datetime::Now();
  const auto driver_id = DriverId(driver_id::DriverDbidView("aaaa"),
                                  driver_id::DriverUuidView("bbbb"));
  auto destination = MakeDestination(Position{11 * lat, 22 * lon}, now,
                                     "super-service", "very-usefull-meta");
  destination.toll_roads = true;

  WatchCommand orig;
  orig.destination = destination;
  orig.driver_id = driver_id;
  orig.type = WatchCommand::Type::kStart;
  orig.orders = {OrderId("order1"), OrderId("order2"), OrderId("order3")};

  const auto fbs = driver_route_watcher::internal::ToFlatbuffers(orig);
  const auto entry = driver_route_watcher::internal::ToWatchCommand(fbs);
  ASSERT_TRUE(::geometry::AreClosePositions(
      orig.destination.ExpressDestinationAsPosition(),
      entry.destination.ExpressDestinationAsPosition()));
  ASSERT_EQ(orig.destination.service_id, entry.destination.service_id);
  ASSERT_EQ(orig.destination.metainfo, entry.destination.metainfo);
  ASSERT_EQ(orig.destination.order_id, entry.destination.order_id);
  ASSERT_LE(orig.destination.timestamp - entry.destination.timestamp,
            std::chrono::seconds(1));
  ASSERT_EQ(orig.driver_id, entry.driver_id);
  ASSERT_EQ(orig.orders, entry.orders);
  ASSERT_TRUE(*entry.destination.toll_roads);
}
