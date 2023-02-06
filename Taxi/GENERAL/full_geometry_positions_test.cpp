#include "full_geometry_positions.hpp"

#include <userver/utest/utest.hpp>

namespace {
using Route = driver_route_watcher::models::Route;
using DriverId = driver_route_watcher::models::DriverId;
using Lat = ::geometry::Latitude;
using Lon = ::geometry::Longitude;
using Position = ::geometry::Position;
using Time = std::chrono::seconds;
using Distance = ::geometry::Distance;
using Azimuth = ::geometry::Azimuth;
using Speed = ::gpssignal::Speed;
using DriverId = driver_route_watcher::models::DriverId;
using driver_route_watcher::internal::BuildFullGeometryPoints;

uint64_t ConvertTimestamp(std::chrono::system_clock::time_point timestamp) {
  return std::chrono::duration_cast<std::chrono::milliseconds>(
             timestamp.time_since_epoch())
      .count();
}
}  // namespace

TEST(BuildFullGeometryPoints, BaseTest) {
  const DriverId kDriverId{driver_id::DriverDbid{"dbid1"},
                           driver_id::DriverUuid{"uuid1"}};
  const ::geobus::types::DriverId kGeobusDriverId{"dbid1_uuid1"};

  const Position kPos1{Lat{55.792159}, Lon{37.596296}};
  const Position kPos2{Lat{55.792569}, Lon{37.601796}};
  const Position kPos3{Lat{55.791009}, Lon{37.602013}};
  const Position kPos4{Lat{55.790835}, Lon{37.599911}};
  const Position kPos5{Lat{55.790127}, Lon{37.597002}};
  const Position kPos6{Lat{55.789091}, Lon{37.597801}};

  const Time kTime1{0};
  const Time kTime2{108};
  const Time kTime3{158};
  const Time kTime4{200};
  const Time kTime5{262};
  const Time kTime6{300};

  const Distance kDist1{0 * ::geometry::meter};
  const Distance kDist2{346 * ::geometry::meter};
  const Distance kDist3{508 * ::geometry::meter};
  const Distance kDist4{641 * ::geometry::meter};
  const Distance kDist5{839 * ::geometry::meter};
  const Distance kDist6{962 * ::geometry::meter};

  const std::string kRouteId = "test_route_id";
  Route route;
  route.route_id = kRouteId;
  route.path = {{kPos1, kTime1, kDist1}, {kPos2, kTime2, kDist2},
                {kPos3, kTime3, kDist3}, {kPos4, kTime4, kDist4},
                {kPos5, kTime5, kDist5}, {kPos6, kTime6, kDist6}};

  const Position kPrevPos{Lat{55.792269}, Lon{37.599088}};
  const std::chrono::system_clock::time_point kPrevTimestamp{
      std::chrono::microseconds{1631529110'000'000}};
  const size_t kPrevSegmentId{0};

  const Position kCurrentPos{Lat{55.790902}, Lon{37.600927}};
  const std::chrono::system_clock::time_point kCurrentTimestamp{
      std::chrono::microseconds{1631529235'000'000}};
  const size_t kCurrentSegmentId{2};

  auto actual = BuildFullGeometryPoints(
      kDriverId, route, kPrevPos, kPrevTimestamp, kPrevSegmentId, kCurrentPos,
      kCurrentTimestamp, kCurrentSegmentId, std::nullopt, std::nullopt, 15.0);

  ASSERT_EQ(actual.size(), 4);

  EXPECT_EQ(actual[0].driver_id, kGeobusDriverId);
  EXPECT_EQ(actual[0].signal.latitude, kPos2.latitude);
  EXPECT_EQ(actual[0].signal.longitude, kPos2.longitude);
  EXPECT_TRUE(actual[0].signal.speed.has_value());
  EXPECT_TRUE(actual[0].signal.direction.has_value());
  EXPECT_NEAR(
      ConvertTimestamp(actual[0].signal.timestamp),
      ConvertTimestamp(kPrevTimestamp + std::chrono::milliseconds{54280}),
      1000);

  EXPECT_EQ(actual[1].driver_id, kGeobusDriverId);
  EXPECT_EQ(actual[1].signal.latitude, actual[0].signal.latitude);
  EXPECT_EQ(actual[1].signal.longitude, actual[0].signal.longitude);
  EXPECT_EQ(actual[1].signal.speed, actual[0].signal.speed);
  EXPECT_EQ(actual[1].signal.direction, actual[2].signal.direction);
  EXPECT_EQ(ConvertTimestamp(actual[1].signal.timestamp),
            ConvertTimestamp(actual[0].signal.timestamp +
                             std::chrono::milliseconds{1}));

  /// Check threshold direction functionality
  EXPECT_TRUE(
      acos(cos(*actual[0].signal.direction - *actual[2].signal.direction)) >
      15.0 * ::geometry::degree);
  EXPECT_EQ(actual[1].signal.direction, actual[2].signal.direction);

  EXPECT_EQ(actual[2].driver_id, kGeobusDriverId);
  EXPECT_EQ(actual[2].signal.latitude, kPos3.latitude);
  EXPECT_EQ(actual[2].signal.longitude, kPos3.longitude);
  EXPECT_TRUE(actual[2].signal.speed.has_value());
  EXPECT_TRUE(actual[2].signal.direction.has_value());
  EXPECT_NEAR(
      ConvertTimestamp(actual[2].signal.timestamp),
      ConvertTimestamp(kPrevTimestamp + std::chrono::milliseconds{104529}),
      1000);

  EXPECT_EQ(actual[3].driver_id, kGeobusDriverId);
  EXPECT_EQ(actual[3].signal.latitude, kCurrentPos.latitude);
  EXPECT_EQ(actual[3].signal.longitude, kCurrentPos.longitude);
  EXPECT_EQ(actual[3].signal.timestamp, kCurrentTimestamp);
  EXPECT_FALSE(actual[3].signal.speed);
  EXPECT_TRUE(actual[3].signal.direction);
}

TEST(BuildFullGeometryPoints, SamePositionsTest) {
  const DriverId kDriverId{driver_id::DriverDbid{"dbid1"},
                           driver_id::DriverUuid{"uuid1"}};
  const ::geobus::types::DriverId kGeobusDriverId{"dbid1_uuid1"};

  const Position kPos1{Lat{55.792159}, Lon{37.596296}};
  const Position kPos2{Lat{55.792569}, Lon{37.601796}};

  const Time kTime1{0};
  const Time kTime2{73};

  const Distance kDist1{0 * ::geometry::meter};
  const Distance kDist2{346 * ::geometry::meter};

  const std::string kRouteId = "test_route_id";
  Route route;
  route.route_id = kRouteId;
  route.path = {{kPos1, kTime1, kDist1}, {kPos2, kTime2, kDist2}};

  const Position kPrevPos{Lat{55.792243}, Lon{37.5997659}};
  const std::chrono::system_clock::time_point kPrevTimestamp{
      std::chrono::microseconds{1631529110'000'000}};
  const size_t kPrevSegmentId{0};

  const Position kCurrentPos{Lat{55.792243}, Lon{37.5997659}};
  const std::chrono::system_clock::time_point kCurrentTimestamp{
      std::chrono::microseconds{1631529152'000'000}};
  const size_t kCurrentSegmentId{0};
  const Speed kCurrentSpeed{10 * ::geometry::meters_per_second};
  const Azimuth kCurrentDirection{123 * ::geometry::degree};

  auto actual = BuildFullGeometryPoints(
      kDriverId, route, kPrevPos, kPrevTimestamp, kPrevSegmentId, kCurrentPos,
      kCurrentTimestamp, kCurrentSegmentId, kCurrentSpeed, kCurrentDirection,
      15.0);

  ASSERT_EQ(actual.size(), 1);

  EXPECT_EQ(actual[0].driver_id, kGeobusDriverId);
  EXPECT_EQ(actual[0].signal.latitude, kCurrentPos.latitude);
  EXPECT_EQ(actual[0].signal.longitude, kCurrentPos.longitude);
  EXPECT_EQ(actual[0].signal.timestamp, kCurrentTimestamp);
  EXPECT_TRUE(actual[0].signal.speed.has_value());
  EXPECT_TRUE(actual[0].signal.direction.has_value());
}

TEST(BuildFullGeometryPoints, SamePositionsWithEmptySegmentsTest) {
  const DriverId kDriverId{driver_id::DriverDbid{"dbid1"},
                           driver_id::DriverUuid{"uuid1"}};
  const ::geobus::types::DriverId kGeobusDriverId{"dbid1_uuid1"};

  const Position kPos1{Lat{55.792159}, Lon{37.596296}};
  const Position kPos2{Lat{55.792159}, Lon{37.596296}};
  const Position kPos3{Lat{55.792159}, Lon{37.596296}};

  const Time kTime1{0};
  const Time kTime2{0};
  const Time kTime3{0};

  const Distance kDist1{0 * ::geometry::meter};
  const Distance kDist2{0 * ::geometry::meter};
  const Distance kDist3{0 * ::geometry::meter};

  const std::string kRouteId = "test_route_id";
  Route route;
  route.route_id = kRouteId;
  route.path = {{kPos1, kTime1, kDist1},
                {kPos2, kTime2, kDist2},
                {kPos3, kTime3, kDist3}};

  const Position kPrevPos{Lat{55.792159}, Lon{37.596296}};
  const std::chrono::system_clock::time_point kPrevTimestamp{
      std::chrono::microseconds{1631529110'000'000}};
  const size_t kPrevSegmentId{0};

  const Position kCurrentPos{Lat{55.792159}, Lon{37.596296}};
  const std::chrono::system_clock::time_point kCurrentTimestamp{
      std::chrono::microseconds{1631529152'000'000}};
  const size_t kCurrentSegmentId{1};
  const Speed kCurrentSpeed{1 * ::geometry::meters_per_second};
  const Azimuth kCurrentDirection{40 * ::geometry::degree};

  auto actual = BuildFullGeometryPoints(
      kDriverId, route, kPrevPos, kPrevTimestamp, kPrevSegmentId, kCurrentPos,
      kCurrentTimestamp, kCurrentSegmentId, kCurrentSpeed, kCurrentDirection,
      15.0);

  ASSERT_EQ(actual.size(), 1);

  EXPECT_EQ(actual[0].driver_id, kGeobusDriverId);
  EXPECT_EQ(actual[0].signal.latitude, kCurrentPos.latitude);
  EXPECT_EQ(actual[0].signal.longitude, kCurrentPos.longitude);
  EXPECT_EQ(actual[0].signal.timestamp, kCurrentTimestamp);
  EXPECT_EQ(actual[0].signal.speed, kCurrentSpeed);
  EXPECT_EQ(actual[0].signal.direction, kCurrentDirection);
}
