#include "route_adjuster.hpp"

#include <geometry/distance.hpp>
#include <geometry/test/geometry_plugin_test.hpp>

#include <userver/crypto/base64.hpp>
#include <userver/utest/utest.hpp>

#include "internal/unittest_utils/test_utils.hpp"
#include "internal/worker/route_joiner.hpp"

namespace {
using driver_route_watcher::models::Position;
using driver_route_watcher::models::Route;
using driver_route_watcher::models::TrackedDestinationPoint;

driver_route_watcher::models::Route MakeRoute(const Position& src,
                                              const Position& dst) {
  static const size_t kIntervals = 100;
  static const auto dt = std::chrono::seconds(100);
  const auto d_lat =
      (dst.latitude - src.latitude) / static_cast<double>(kIntervals);
  const auto d_lon =
      (dst.longitude - src.longitude) / static_cast<double>(kIntervals);

  driver_route_watcher::models::Route ret;
  auto& path = ret.path;
  path.reserve(kIntervals + 1);

  for (size_t i = 0; i < kIntervals + 1; ++i) {
    clients::routing::RoutePoint p;
    p.latitude = src.latitude + static_cast<double>(i) * d_lat;
    p.longitude = src.longitude + static_cast<double>(i) * d_lon;
    p.distance_since_ride_start = GreatCircleDistance(src, p);
    p.time_since_ride_start = i * dt;

    path.push_back(p);
  }
  ret.info.distance = path.back().distance_since_ride_start;
  ret.info.time = path.back().time_since_ride_start;
  ret.info.blocked = false;
  ret.legs.push_back({0});

  return ret;
}

driver_route_watcher::models::Route MakeReturningOverlappingRoute() {
  // static const size_t kIntervals = 100;
  static const auto dt = std::chrono::seconds(100);
  static const auto kSpeed = 40. * ::geometry::km_per_hour;
  const Position point = {37 * ::geometry::lon, 55 * ::geometry::lat};

  driver_route_watcher::models::Route ret;
  auto& path = ret.path;
  path.reserve(13);

  clients::routing::RoutePoint p;
  {
    p.latitude = point.latitude;
    p.longitude = point.longitude;
    p.distance_since_ride_start = 0 * ::geometry::meter;
    // kSpeed.value() * (i * dt.count()) *
    p.time_since_ride_start = 0 * dt;
    path.push_back(p);
  }

  for (size_t i = 0; i < 5; ++i) {
    p.longitude += geometry::LongitudeDelta(0.001);
    p.distance_since_ride_start +=
        dt.count() * kSpeed.value() * geometry::meter;
    p.time_since_ride_start += dt;
    path.push_back(p);
  }
  for (size_t i = 0; i < 8; ++i) {
    p.longitude -= geometry::LongitudeDelta(0.001);
    p.distance_since_ride_start +=
        dt.count() * kSpeed.value() * geometry::meter;
    p.time_since_ride_start += dt;
    path.push_back(p);
  }

  ret.info.distance = path.back().distance_since_ride_start;
  ret.info.time = path.back().time_since_ride_start;
  ret.info.blocked = false;
  ret.legs.push_back({0});

  return ret;
}

driver_route_watcher::models::DriverPosition MakeDriverPosition(
    const driver_route_watcher::models::Position& pos) {
  driver_route_watcher::models::DriverPosition ret(
      pos.latitude, pos.longitude,
      driver_route_watcher::models::TransportType::kCar,
      driver_route_watcher::models::Adjusted::kNo);
  return ret;
}
const size_t kMaxAdjustCandidates = 2;
const bool kTreatNegativeAsFailed = false;

}  // namespace

TEST(route_adjuster, empty) {
  using namespace ::geometry::literals;
  const auto kMaxDistance = 100 * ::geometry::meter;

  ::driver_route_watcher::internal::RouteAdjuster adjuster;

  // Do not fail
  auto time_left_none =
      adjuster.Adjust(MakeDriverPosition({37._lat, 55._lon}), kMaxDistance,
                      kMaxAdjustCandidates, kTreatNegativeAsFailed, {});
  EXPECT_EQ(std::nullopt, time_left_none);
}

/// When driver is near first control point and has negative eta, than return
/// first control point
TEST(route_adjuster, base_test) {
  using driver_route_watcher::test_utils::MakeTrackedDestinationPoint;
  using namespace ::geometry::literals;

  const auto kMaxDistance = 100 * ::geometry::meter;

  auto TestPositionsAreClose = [](const auto& p1, const auto& p2) {
    ::geometry::test::GeometryTestPlugin::TestPositionsAreClose(p1, p2);
  };

  const auto src = ::geometry::Position(37._lon, 55._lat);
  const auto dst = ::geometry::Position(37.1_lon, 55.1_lat);
  const auto route = MakeRoute(src, dst);
  const auto& path = route.path;
  const auto& start = path.front();
  const auto& end = path.back();
  const auto& middle_point = route.path[path.size() / 2];
  const auto& route_time = end.time_since_ride_start;
  const auto& route_distance = end.distance_since_ride_start;

  EXPECT_EQ(static_cast<::geometry::Position>(route.path.front()), src);
  EXPECT_EQ(::geometry::Position(route.path.back()), dst);
  EXPECT_EQ(::geometry::Position(37.05_lon, 55.05_lat),
            static_cast<::geometry::Position>(middle_point));

  EXPECT_NEAR(route_distance.value(), route.info.distance->value(), 1.0);
  EXPECT_NEAR(route_time.count(), route.info.time->count(), 1.0);

  ::driver_route_watcher::internal::RouteAdjuster adjuster;

  {
    adjuster.SetRoute(route, {dst}, kMaxDistance);
    // first point
    const auto adjusted = adjuster.Adjust(
        MakeDriverPosition(start), kMaxDistance, kMaxAdjustCandidates,
        kTreatNegativeAsFailed, MakeTrackedDestinationPoint(dst));
    ASSERT_TRUE(adjusted != std::nullopt);
    TestPositionsAreClose(
        adjusted->GetTrackedDestinationPoints().front().GetPosition(), dst);
    TestPositionsAreClose(adjusted->GetAdjustedPosition(), start);
    EXPECT_NEAR(adjusted->GetEta().distance_left.value(),
                route_distance.value(), 1.0);
    EXPECT_NEAR(adjusted->GetEta().time_left.count(), route_time.count(), 1.0);
  }

  {
    adjuster.SetRoute(route, {dst}, kMaxDistance);
    // last point
    const auto adjusted = adjuster.Adjust(
        MakeDriverPosition(end), kMaxDistance, kMaxAdjustCandidates,
        kTreatNegativeAsFailed, MakeTrackedDestinationPoint(dst));
    ASSERT_TRUE(adjusted != std::nullopt);
    TestPositionsAreClose(
        adjusted->GetTrackedDestinationPoints().front().GetPosition(), dst);
    TestPositionsAreClose(adjusted->GetAdjustedPosition(), end);
    EXPECT_EQ(adjusted->GetEta().distance_left, 0 * ::geometry::meter);
    EXPECT_EQ(adjusted->GetEta().time_left, std::chrono::seconds(0));
  }

  {
    adjuster.SetRoute(route, {dst}, kMaxDistance);

    // middle point
    const auto adjusted = adjuster.Adjust(
        MakeDriverPosition(middle_point), kMaxDistance, kMaxAdjustCandidates,
        kTreatNegativeAsFailed, MakeTrackedDestinationPoint(dst));
    ASSERT_TRUE(adjusted != std::nullopt);
    TestPositionsAreClose(
        adjusted->GetTrackedDestinationPoints().front().GetPosition(), dst);
    TestPositionsAreClose(adjusted->GetAdjustedPosition(), middle_point);

    EXPECT_NEAR(adjusted->GetEta().distance_left.value(),
                route_distance.value() * 0.5, 2.0);
    EXPECT_NEAR(adjusted->GetEta().time_left.count(), route_time.count() * 0.5,
                1.0);
  }

  {
    // far point
    const auto far_point = ::geometry::Position(38._lon, 55._lat);
    const auto adjusted = adjuster.Adjust(
        MakeDriverPosition(far_point), kMaxDistance, kMaxAdjustCandidates,
        kTreatNegativeAsFailed, MakeTrackedDestinationPoint(dst));
    ASSERT_TRUE(adjusted == std::nullopt);
  }

  {
    // far point (found cause MaxDistance increased)
    const auto far_point = ::geometry::Position(38._lon, 55._lat);
    const auto adjusted =
        adjuster.Adjust(MakeDriverPosition(far_point), 1000 * kMaxDistance,
                        kMaxAdjustCandidates, kTreatNegativeAsFailed,
                        MakeTrackedDestinationPoint(dst));
    ASSERT_FALSE(adjusted == std::nullopt);
  }
}

TEST(route_adjuster, many_destinations_test) {
  using driver_route_watcher::test_utils::MakeTrackedDestinationPoint;
  using namespace ::geometry::literals;

  const auto kMaxDistance = 100 * ::geometry::meter;

  auto TestPositionsAreClose = [](const auto& p1, const auto& p2) {
    ::geometry::test::GeometryTestPlugin::TestPositionsAreClose(p1, p2);
  };

  const auto src = ::geometry::Position(37._lon, 55._lat);
  const auto dst_1 = ::geometry::Position(37.1_lon, 55.1_lat);
  const auto dst_2 = ::geometry::Position(37.1_lon, 55.2_lat);
  const auto route1 = MakeRoute(src, dst_1);
  const auto route2 = MakeRoute(dst_1, dst_2);
  const auto route =
      driver_route_watcher::internal::UniteRoutes({route1, route2});

  std::vector<TrackedDestinationPoint> tracked_points =
      MakeTrackedDestinationPoint(dst_1);
  tracked_points.push_back(MakeTrackedDestinationPoint(dst_2).back());

  ::driver_route_watcher::internal::RouteAdjuster adjuster;

  size_t max_adjust_candidates = 5;
  bool treat_negative_as_failed = true;
  {
    adjuster.SetRoute(route);
    // point near dst_1 (~50m)
    const auto adjusted = adjuster.Adjust(
        MakeDriverPosition(::geometry::Position(37.1_lon, 55.1005_lat)),
        kMaxDistance, max_adjust_candidates, treat_negative_as_failed,
        tracked_points);
    ASSERT_TRUE(adjusted != std::nullopt);
    TestPositionsAreClose(
        adjusted->GetTrackedDestinationPoints().front().GetPosition(), dst_1);
    TestPositionsAreClose(
        adjusted->GetTrackedDestinationPoints().back().GetPosition(), dst_2);
    TestPositionsAreClose(adjusted->GetAdjustedPosition(), dst_1);
    EXPECT_EQ(adjusted->GetEtas()[0].distance_left, 0 * ::geometry::meter);
    EXPECT_EQ(adjusted->GetEtas()[0].time_left, std::chrono::seconds(0));
    EXPECT_EQ(adjusted->GetDirection(), ::geometry::Azimuth::from_value(0));
  }

  {
    adjuster.SetRoute(route);
    // far point
    const auto adjusted = adjuster.Adjust(
        MakeDriverPosition(::geometry::Position(37.1_lon, 55.15_lat)),
        kMaxDistance, max_adjust_candidates, treat_negative_as_failed,
        tracked_points);
    ASSERT_TRUE(adjusted == std::nullopt);
  }
}

TEST(route_adjuster, base_with_legs) {
  using driver_route_watcher::test_utils::MakeTrackedDestinationPoint;
  using namespace ::geometry::literals;

  const auto kMaxDistance = 100 * ::geometry::meter;

  auto TestPositionsAreClose = [](const auto& p1, const auto& p2) {
    ::geometry::test::GeometryTestPlugin::TestPositionsAreClose(p1, p2);
  };

  const auto src = ::geometry::Position(37._lon, 55._lat);
  const auto dst = ::geometry::Position(37.1_lon, 55.1_lat);
  const auto route = MakeRoute(src, dst);
  const auto& path = route.path;
  const auto& start = path.front();
  const auto& end = path.back();
  const auto& middle_point = route.path[path.size() / 2];
  const auto& route_time = end.time_since_ride_start;
  const auto& route_distance = end.distance_since_ride_start;

  EXPECT_EQ(static_cast<::geometry::Position>(route.path.front()), src);
  EXPECT_EQ(::geometry::Position(route.path.back()), dst);
  EXPECT_EQ(::geometry::Position(37.05_lon, 55.05_lat),
            static_cast<::geometry::Position>(middle_point));

  EXPECT_NEAR(route_distance.value(), route.info.distance->value(), 1.0);
  EXPECT_NEAR(route_time.count(), route.info.time->count(), 1.0);

  ::driver_route_watcher::internal::RouteAdjuster adjuster;

  {
    adjuster.SetRoute(route);
    // first point
    const auto adjusted = adjuster.Adjust(
        MakeDriverPosition(start), kMaxDistance, kMaxAdjustCandidates,
        kTreatNegativeAsFailed, {MakeTrackedDestinationPoint(dst)});
    ASSERT_TRUE(adjusted != std::nullopt);
    TestPositionsAreClose(
        adjusted->GetTrackedDestinationPoints().back().GetPosition(), dst);
    TestPositionsAreClose(adjusted->GetAdjustedPosition(), start);
    EXPECT_NEAR(adjusted->GetEta().distance_left.value(),
                route_distance.value(), 1.0);
    EXPECT_NEAR(adjusted->GetEta().time_left.count(), route_time.count(), 1.0);
  }

  {
    adjuster.SetRoute(route);
    // last point
    const auto adjusted = adjuster.Adjust(
        MakeDriverPosition(end), kMaxDistance, kMaxAdjustCandidates,
        kTreatNegativeAsFailed, {MakeTrackedDestinationPoint(dst)});
    ASSERT_TRUE(adjusted != std::nullopt);
    TestPositionsAreClose(
        adjusted->GetTrackedDestinationPoints().back().GetPosition(), dst);
    TestPositionsAreClose(adjusted->GetAdjustedPosition(), end);
    EXPECT_EQ(adjusted->GetEta().distance_left, 0 * ::geometry::meter);
    EXPECT_EQ(adjusted->GetEta().time_left, std::chrono::seconds(0));
    EXPECT_EQ(adjusted->GetEtas().size(), 1ull);
  }

  {
    adjuster.SetRoute(route);

    // middle point
    const auto adjusted = adjuster.Adjust(
        MakeDriverPosition(middle_point), kMaxDistance, kMaxAdjustCandidates,
        kTreatNegativeAsFailed, {MakeTrackedDestinationPoint(dst)});
    ASSERT_TRUE(adjusted != std::nullopt);
    TestPositionsAreClose(
        adjusted->GetTrackedDestinationPoints().back().GetPosition(), dst);
    TestPositionsAreClose(adjusted->GetAdjustedPosition(), middle_point);

    EXPECT_NEAR(adjusted->GetEta().distance_left.value(),
                route_distance.value() * 0.5, 2.0);
    EXPECT_NEAR(adjusted->GetEta().time_left.count(), route_time.count() * 0.5,
                1.0);
    EXPECT_EQ(adjusted->GetEtas().size(), 1ull);
  }

  {
    // far point
    const auto far_point = ::geometry::Position(38._lon, 55._lat);
    const auto adjusted = adjuster.Adjust(
        MakeDriverPosition(far_point), kMaxDistance, kMaxAdjustCandidates,
        kTreatNegativeAsFailed, {MakeTrackedDestinationPoint(dst)});
    ASSERT_TRUE(adjusted == std::nullopt);
  }

  {
    // far point (found cause MaxDistance increased)
    const auto far_point = ::geometry::Position(38._lon, 55._lat);
    const auto adjusted =
        adjuster.Adjust(MakeDriverPosition(far_point), 1000 * kMaxDistance,
                        kMaxAdjustCandidates, kTreatNegativeAsFailed,
                        {MakeTrackedDestinationPoint(dst)});
    ASSERT_FALSE(adjusted == std::nullopt);
  }
}

TEST(route_adjuster, no_negative_etas) {
  using driver_route_watcher::test_utils::MakeTrackedDestinationPoint;
  using namespace ::geometry::literals;

  const auto kMaxDistance = 100 * ::geometry::meter;

  auto TestPositionsAreClose = [](const auto& p1, const auto& p2) {
    ::geometry::test::GeometryTestPlugin::TestPositionsAreClose(p1, p2);
  };

  const auto src = ::geometry::Position(37._lon, 55._lat);
  const auto dst = ::geometry::Position(37.1_lon, 55.1_lat);
  // route_dst not equals requested dst so route become slightly longer
  const auto route_dst = ::geometry::Position(37.11_lon, 55.11_lat);
  const auto route = MakeRoute(src, route_dst);
  const auto& path = route.path;
  const auto& end = path.back();
  const auto& route_time = end.time_since_ride_start;
  const auto& route_distance = end.distance_since_ride_start;

  EXPECT_EQ(static_cast<::geometry::Position>(route.path.front()), src);
  EXPECT_EQ(::geometry::Position(route.path.back()), route_dst);

  EXPECT_NEAR(route_distance.value(), route.info.distance->value(), 1.0);
  EXPECT_NEAR(route_time.count(), route.info.time->count(), 1.0);

  ::driver_route_watcher::internal::RouteAdjuster adjuster;

  {
    adjuster.SetRoute(route, {dst}, kMaxDistance);
    // first point
    const auto adjusted = adjuster.Adjust(
        MakeDriverPosition(route_dst), kMaxDistance, kMaxAdjustCandidates,
        kTreatNegativeAsFailed, {MakeTrackedDestinationPoint(dst)});
    ASSERT_TRUE(adjusted != std::nullopt);
    TestPositionsAreClose(
        adjusted->GetTrackedDestinationPoints().back().GetPosition(), dst);
    TestPositionsAreClose(adjusted->GetAdjustedPosition(), route_dst);
    EXPECT_EQ(adjusted->GetEta().distance_left, 0 * geometry::meter);
    EXPECT_EQ(adjusted->GetEta().time_left, std::chrono::seconds(0));
  }
}

TEST(route_adjuster, overlapping_returning) {
  using driver_route_watcher::test_utils::MakeTrackedDestinationPoint;
  using namespace ::geometry::literals;

  const auto kMaxDistance = 1000 * ::geometry::meter;

  auto TestPositionsAreClose = [](const auto& p1, const auto& p2) {
    ::geometry::test::GeometryTestPlugin::TestPositionsAreClose(p1, p2);
  };

  const auto src = ::geometry::Position(37._lon, 55._lat);
  const auto dst = ::geometry::Position(36.997_lon, 55._lat);
  const auto route = MakeReturningOverlappingRoute();
  const auto& path = route.path;
  const auto& start = path.front();
  const auto& end = path.back();
  const auto& route_time = end.time_since_ride_start;
  const auto& route_distance = end.distance_since_ride_start;

  EXPECT_EQ(static_cast<::geometry::Position>(route.path.front()), src);
  TestPositionsAreClose(::geometry::Position(route.path.back()), dst);

  EXPECT_NEAR(route_distance.value(), route.info.distance->value(), 1.0);
  EXPECT_NEAR(route_time.count(), route.info.time->count(), 1.0);

  ::driver_route_watcher::internal::RouteAdjuster adjuster;

  {
    /// Default settings
    /// Adjust to end, cause 2 nearest edges of route located near end of route
    const size_t kMaxAdjustCandidates = 2;
    adjuster.SetRoute(route, {dst}, kMaxDistance);
    // first point
    const auto adjusted = adjuster.Adjust(
        MakeDriverPosition(dst), kMaxDistance, kMaxAdjustCandidates,
        kTreatNegativeAsFailed, {MakeTrackedDestinationPoint(dst)});
    ASSERT_TRUE(adjusted != std::nullopt);
    TestPositionsAreClose(
        adjusted->GetTrackedDestinationPoints().back().GetPosition(), dst);
    TestPositionsAreClose(adjusted->GetAdjustedPosition(), end);
    EXPECT_EQ(adjusted->GetEta().distance_left, 0 * geometry::meter);
    EXPECT_EQ(adjusted->GetEta().time_left, std::chrono::seconds(0));
  }
  {
    /// Default settings
    /// Adjust to start, cause some of nearest edges located near end and some
    /// near start, then choose nearest from first group of edges before gap
    const size_t kMaxAdjustCandidates = 5;
    adjuster.SetRoute(route, {dst}, kMaxDistance);
    // first point
    const auto adjusted = adjuster.Adjust(
        MakeDriverPosition(dst), kMaxDistance, kMaxAdjustCandidates,
        kTreatNegativeAsFailed, {MakeTrackedDestinationPoint(dst)});
    ASSERT_TRUE(adjusted != std::nullopt);
    TestPositionsAreClose(
        adjusted->GetTrackedDestinationPoints().back().GetPosition(), dst);
    TestPositionsAreClose(adjusted->GetAdjustedPosition(), start);
    EXPECT_EQ(adjusted->GetEta().distance_left, route_distance);
    EXPECT_EQ(adjusted->GetEta().time_left, route_time);
  }
}

/// When driver pass intemediate point (and so has negative eta)
/// treat this case as failed adjust
TEST(route_adjuster, negative_intermediate_etas) {
  using driver_route_watcher::test_utils::MakeTrackedDestinationPoint;
  using namespace ::geometry::literals;

  const auto kMaxDistance = 100 * ::geometry::meter;

  auto TestPositionsAreClose = [](const auto& p1, const auto& p2) {
    ::geometry::test::GeometryTestPlugin::TestPositionsAreClose(p1, p2);
  };

  const auto src = ::geometry::Position(37._lon, 55._lat);
  const auto dst = ::geometry::Position(37.1_lon, 55.1_lat);
  const auto route = MakeRoute(src, dst);
  const auto& path = route.path;
  const auto& end = path.back();
  const auto& middle_point = route.path[path.size() / 2];
  const auto& route_time = end.time_since_ride_start;
  const auto& route_distance = end.distance_since_ride_start;

  ::geometry::Position before_mid =
      middle_point - ::geometry::PositionDelta(geometry::LatitudeDelta(0.01),
                                               geometry::LongitudeDelta(0.01));
  ::geometry::Position after_mid =
      middle_point + ::geometry::PositionDelta(geometry::LatitudeDelta(0.01),
                                               geometry::LongitudeDelta(0.01));

  EXPECT_EQ(static_cast<::geometry::Position>(route.path.front()), src);
  EXPECT_EQ(::geometry::Position(route.path.back()), dst);
  EXPECT_EQ(::geometry::Position(37.05_lon, 55.05_lat),
            static_cast<::geometry::Position>(middle_point));

  EXPECT_NEAR(route_distance.value(), route.info.distance->value(), 1.0);
  EXPECT_NEAR(route_time.count(), route.info.time->count(), 1.0);

  ::driver_route_watcher::internal::RouteAdjuster adjuster;

  const bool kTreatNegativeAsFailed = true;
  {
    adjuster.SetRoute(route, {middle_point, dst}, kMaxDistance);
    // first point before middle point should be adjusted
    const auto adjusted = adjuster.Adjust(
        MakeDriverPosition(before_mid), kMaxDistance, kMaxAdjustCandidates,
        kTreatNegativeAsFailed, {MakeTrackedDestinationPoint(dst)});
    ASSERT_TRUE(adjusted != std::nullopt);
    TestPositionsAreClose(
        adjusted->GetTrackedDestinationPoints().back().GetPosition(), dst);
    TestPositionsAreClose(adjusted->GetAdjustedPosition(), before_mid);
    EXPECT_EQ(2ull, adjusted->GetEtas().size());
    EXPECT_NEAR(adjusted->GetEta().distance_left.value(), 7688, 1.0);
    EXPECT_NEAR(adjusted->GetEta().time_left.count(), 6000, 1.0);
    EXPECT_NEAR(adjusted->GetEtas().at(0).distance_left.value(), 1281, 1.0);
    EXPECT_NEAR(adjusted->GetEtas().at(0).time_left.count(), 1000, 1.0);
  }
  {
    adjuster.SetRoute(route, {middle_point, dst}, kMaxDistance);
    // second point after middle point should NOT be adjusted
    // so we have to rebuild our route
    const auto adjusted = adjuster.Adjust(
        MakeDriverPosition(after_mid), kMaxDistance, kMaxAdjustCandidates,
        kTreatNegativeAsFailed, {MakeTrackedDestinationPoint(dst)});
    ASSERT_TRUE(adjusted == std::nullopt);
  }
}
