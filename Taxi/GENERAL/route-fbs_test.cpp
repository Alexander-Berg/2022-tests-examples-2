#include <gtest/gtest.h>
#include <routing-base-fbs/route-fbs.hpp>

namespace {
routing_base::RoutePath MakePath() {
  routing_base::RoutePath path;
  path.info.blocked = true;
  path.info.distance = 100500 * ::geometry::meter;
  path.info.time = std::chrono::seconds(4242);

  path.path.push_back(::routing_base::RoutePoint(
      {10 * geometry::lat, 77 * geometry::lon}, std::chrono::seconds(0),
      0 * ::geometry::meter));
  path.path.push_back(::routing_base::RoutePoint(
      {22 * geometry::lat, 33 * geometry::lon}, std::chrono::seconds(10),
      100 * ::geometry::meter));
  path.path.push_back(::routing_base::RoutePoint(
      {44 * geometry::lat, 55 * geometry::lon}, std::chrono::seconds(20),
      200 * ::geometry::meter));

  path.legs.push_back({0});
  path.legs.push_back({1});

  return path;
}
}  // namespace

TEST(route_fbs, base) {
  const auto orig = MakePath();
  const auto data = ::routing_base::fbs::ToFlatbuffers(orig);
  const auto route = ::routing_base::fbs::ToRoutePath(data);
  ASSERT_EQ(orig.info.blocked, route.info.blocked);
  ASSERT_EQ(orig.info.distance, route.info.distance);
  ASSERT_EQ(orig.info.time, route.info.time);

  ASSERT_EQ(orig.path.size(), route.path.size());
  for (size_t i = 0; i < orig.path.size(); ++i) {
    const auto& orig_point = orig.path[i];
    const auto& route_point = route.path[i];
    ASSERT_TRUE(::geometry::AreClosePositions(orig_point, route_point));
    ASSERT_EQ(orig_point.distance_since_ride_start,
              route_point.distance_since_ride_start);
    ASSERT_EQ(orig_point.time_since_ride_start,
              route_point.time_since_ride_start);
  }

  ASSERT_EQ(orig.legs.size(), route.legs.size());
  for (size_t i = 0; i < orig.legs.size(); ++i) {
    EXPECT_EQ(orig.legs[i].point_index, route.legs[i].point_index);
  }
}

TEST(route_fbs, route_id) {
  auto orig = MakePath();
  orig.route_id = "route_id";

  const auto data = ::routing_base::fbs::ToFlatbuffers(orig);
  const auto route = ::routing_base::fbs::ToRoutePath(data);
  ASSERT_EQ(orig.route_id, route.route_id);
}

TEST(route_fbs, route_source) {
  {
    auto orig = MakePath();
    orig.info.route_source = routing_base::RouteSource::kUnknown;

    const auto data = ::routing_base::fbs::ToFlatbuffers(orig);
    const auto route = ::routing_base::fbs::ToRoutePath(data);
    ASSERT_EQ(orig.info.route_source, route.info.route_source);
  }

  {
    auto orig = MakePath();
    orig.info.route_source = routing_base::RouteSource::kYandexMaps;

    const auto data = ::routing_base::fbs::ToFlatbuffers(orig);
    const auto route = ::routing_base::fbs::ToRoutePath(data);
    ASSERT_EQ(orig.info.route_source, route.info.route_source);
  }

  {
    auto orig = MakePath();
    orig.info.route_source = routing_base::RouteSource::kTigraph;

    const auto data = ::routing_base::fbs::ToFlatbuffers(orig);
    const auto route = ::routing_base::fbs::ToRoutePath(data);
    ASSERT_EQ(orig.info.route_source, route.info.route_source);
  }

  {
    auto orig = MakePath();
    orig.info.route_source = routing_base::RouteSource::kGoogle;

    const auto data = ::routing_base::fbs::ToFlatbuffers(orig);
    const auto route = ::routing_base::fbs::ToRoutePath(data);
    ASSERT_EQ(orig.info.route_source, route.info.route_source);
  }

  {
    auto orig = MakePath();
    orig.info.route_source = routing_base::RouteSource::kLinearFallback;

    const auto data = ::routing_base::fbs::ToFlatbuffers(orig);
    const auto route = ::routing_base::fbs::ToRoutePath(data);
    ASSERT_EQ(orig.info.route_source, route.info.route_source);
  }
}
