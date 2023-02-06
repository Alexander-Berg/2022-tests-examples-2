#include "stq_task_parser.hpp"

#include <gtest/gtest.h>

::geometry::Position MakePos(double val) {
  return ::geometry::Position{val * ::geometry::lat, val * ::geometry::lon};
}

TEST(stq_task_parser, new_dst) {
  const std::vector<::geometry::Position> destinations = {MakePos(11),
                                                          MakePos(22)};
  const std::vector<bool> statuses = {};

  const auto ret =
      driver_route_watcher::internal::NormalizeRequestWithDestinations(
          destinations, statuses, false);
  ASSERT_TRUE(::geometry::AreClosePositions(ret, MakePos(11)));
}

TEST(stq_task_parser, new_dst_1_passed) {
  const std::vector<::geometry::Position> destinations = {MakePos(11),
                                                          MakePos(22)};
  std::vector<bool> statuses;
  statuses.push_back(true);

  const auto ret =
      driver_route_watcher::internal::NormalizeRequestWithDestinations(
          destinations, statuses, false);
  ASSERT_TRUE(::geometry::AreClosePositions(ret, MakePos(22)));
}

TEST(stq_task_parser, new_dst_2_passed) {
  const std::vector<::geometry::Position> destinations = {MakePos(11),
                                                          MakePos(22)};
  std::vector<bool> statuses;
  statuses.push_back(true);
  statuses.push_back(true);

  EXPECT_ANY_THROW(
      driver_route_watcher::internal::NormalizeRequestWithDestinations(
          destinations, statuses, false));
}

TEST(stq_task_parser, new_dst_1_false) {
  const std::vector<::geometry::Position> destinations = {MakePos(11),
                                                          MakePos(22)};
  std::vector<bool> statuses;
  statuses.push_back(false);

  const auto ret =
      driver_route_watcher::internal::NormalizeRequestWithDestinations(
          destinations, statuses, false);
  ASSERT_TRUE(::geometry::AreClosePositions(ret, MakePos(11)));
}

TEST(stq_task_parser, new_dst_2_false) {
  const std::vector<::geometry::Position> destinations = {MakePos(11),
                                                          MakePos(22)};
  std::vector<bool> statuses;
  statuses.push_back(false);
  statuses.push_back(false);

  const auto ret =
      driver_route_watcher::internal::NormalizeRequestWithDestinations(
          destinations, statuses, false);
  ASSERT_TRUE(::geometry::AreClosePositions(ret, MakePos(11)));
}

TEST(stq_task_parser, reset_dst_2_passed) {
  const std::vector<::geometry::Position> destinations = {MakePos(11),
                                                          MakePos(22)};
  std::vector<bool> statuses;
  statuses.push_back(true);
  statuses.push_back(true);

  const auto ret =
      driver_route_watcher::internal::NormalizeRequestWithDestinations(
          destinations, statuses, true);
  ASSERT_TRUE(::geometry::AreClosePositions(ret, MakePos(22)));
}

TEST(stq_task_parser, destinations_not_passed) {
  const std::vector<::geometry::Position> destinations = {MakePos(11),
                                                          MakePos(22)};
  std::vector<bool> statuses;
  statuses.push_back(false);
  statuses.push_back(false);

  const auto ret = driver_route_watcher::internal::NormalizeRequestDestinations(
      destinations, statuses);
  ASSERT_EQ(ret, destinations);
}

TEST(stq_task_parser, destinations_not_passed_2) {
  const std::vector<::geometry::Position> destinations = {MakePos(11),
                                                          MakePos(22)};
  std::vector<bool> statuses;

  const auto ret = driver_route_watcher::internal::NormalizeRequestDestinations(
      destinations, statuses);
  ASSERT_EQ(ret, destinations);
}

TEST(stq_task_parser, destinations_passed) {
  const std::vector<::geometry::Position> destinations = {MakePos(11),
                                                          MakePos(22)};
  std::vector<bool> statuses;
  statuses.push_back(true);
  statuses.push_back(false);

  const auto ret = driver_route_watcher::internal::NormalizeRequestDestinations(
      destinations, statuses);
  ASSERT_EQ(1ul, ret.size());
  ASSERT_TRUE(::geometry::AreClosePositions(ret.front(), MakePos(22)));
}

TEST(stq_task_parser, destinations_all_passed) {
  const std::vector<::geometry::Position> destinations = {MakePos(11),
                                                          MakePos(22)};
  std::vector<bool> statuses;
  statuses.push_back(true);
  statuses.push_back(true);

  const auto ret = driver_route_watcher::internal::NormalizeRequestDestinations(
      destinations, statuses);
  ASSERT_TRUE(ret.empty());
}
