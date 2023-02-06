#include <userver/utest/utest.hpp>

#include <geometry/units.hpp>
#include <routing-base/route_info.hpp>
#include <routing-base/test/print_to.hpp>
#include <routing-base/test/routing_base_generator.hpp>

namespace routing_base {

struct RoutePathFixture : public testing::Test,
                          public test::RoutingBaseGenerator {};

TEST_F(RoutePathFixture, EmptyView) {
  RoutePathView empty;
  RoutePath result{empty};

  EXPECT_TRUE(result.info.Empty());
  EXPECT_TRUE(result.path.empty());
}

TEST_F(RoutePathFixture, Self) {
  using namespace geometry::literals;

  RoutePath data = CreateRoutePath(std::chrono::seconds(42), 42.0_meters, 3, 5);

  RoutePath copy = RoutePath{data.ToView()};

  EXPECT_EQ(data.path, copy.path);
}

TEST_F(RoutePathFixture, Overview) {
  using namespace geometry::literals;

  constexpr size_t kLegsCount = 3;

  RoutePath data =
      CreateRoutePath(std::chrono::seconds(42), 42.0_meters, kLegsCount, 5);

  const auto overview = data.GetLegsOverview();

  EXPECT_EQ(kLegsCount, overview.size());

  // check that views overlap
  for (size_t i = 1; i < overview.size(); ++i) {
    const auto& current = overview[i];
    const auto& prev = overview[i - 1];

    // last element of prev and first elemnet of next must be same element
    EXPECT_EQ(current.front(), prev.back());
  }
}

TEST_F(RoutePathFixture, SubviewToPath) {
  using namespace geometry::literals;

  constexpr size_t kLegsCount = 3;

  RoutePath data =
      CreateRoutePath(std::chrono::seconds(42), 42.0_meters, kLegsCount, 5);

  const auto overview = data.GetLegsOverview();

  // every leg after first one will start with '0' time/distance since ride
  for (size_t i = 1; i < overview.size(); ++i) {
    auto path = RoutePath{overview[i]};

    EXPECT_EQ(0, path.path.at(0).time_since_ride_start.count()) << "leg: " << i;
    EXPECT_EQ(0, path.path.at(0).distance_since_ride_start.value())
        << "leg: " << i;
  }
  // and time_since_ride_start for first element is equal to original
  EXPECT_EQ(data.path[0], RoutePath{overview[0]}.path[0]);

  // sum of all generated route_info must be equal to original route_info
  Time accum_time{0};
  Distance accum_distance = 0.0_meters;
  for (size_t i = 0; i < overview.size(); ++i) {
    auto path = RoutePath{overview[i]};

    ASSERT_TRUE(path.info.time);
    accum_time += *(path.info.time);

    ASSERT_TRUE(path.info.distance);
    accum_distance += *(path.info.distance);
  }

  ASSERT_TRUE(data.info.time);
  EXPECT_EQ(accum_time, *data.info.time);
  ASSERT_TRUE(data.info.distance);
  EXPECT_DOUBLE_EQ(accum_distance.value(), data.info.distance->value());
}

TEST_F(RoutePathFixture, SubviewsToPath) {
  using namespace geometry::literals;

  constexpr size_t kLegsCount = 3;

  RoutePath data =
      CreateRoutePath(std::chrono::seconds(42), 42.0_meters, kLegsCount, 5);

  const auto overview = data.GetLegsOverview();

  auto path = RoutePath(overview.begin(), overview.end());

  // time_since_ride_start for first element is equal to original
  EXPECT_EQ(data.path[0], path.path[0]);

  // legs must be equal
  EXPECT_EQ(path.legs.size(), data.legs.size());
  for (size_t i = 0; i < std::min(path.legs.size(), data.legs.size()); ++i) {
    EXPECT_EQ(path.legs[i].point_index, path.legs[i].point_index);
  }

  // paths must be equal
  EXPECT_EQ(path.path.size(), data.path.size());
  for (size_t i = 0; i < std::min(path.path.size(), data.path.size()); ++i) {
    EXPECT_EQ(path.path[i], data.path[i]);
  }

  // route info's time and distance must be equal
  EXPECT_EQ(path.info.time, data.info.time);
  EXPECT_EQ(path.info.distance, data.info.distance);
}

}  // namespace routing_base
