#include "route_predicted_positions.hpp"

#include <geometry/intermediate_point.hpp>

#include <userver/utest/utest.hpp>

namespace {

using Route = driver_route_watcher::models::Route;
using Lat = ::geometry::Latitude;
using Lon = ::geometry::Longitude;
using Position = ::geometry::Position;
using Time = std::chrono::seconds;
using Distance = ::geometry::Distance;
using Azimuth = ::geometry::Azimuth;
using Speed = ::gpssignal::Speed;
using Eta = driver_route_watcher::models::Eta;
using TrackingType = driver_route_watcher::models::TrackingType;
using driver_route_watcher::internal::GetRoutePredictedPosition;
}  // namespace

TEST(PredictPosition, EndOfRouteTest) {
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

  const Eta kEta = {std::chrono::seconds{138}, 543 * ::geometry::meter,
                    TrackingType::kRouteTracking};
  const size_t kSegmentIdx = 2;
  const std::chrono::system_clock::time_point kTimestamp{
      std::chrono::seconds{2134543}};
  const std::chrono::seconds kPeriod{150};

  auto actual = GetRoutePredictedPosition(route, {kEta}, kSegmentIdx,
                                          kTimestamp, kPeriod);

  ASSERT_TRUE(actual);
  EXPECT_EQ(actual->prediction_shift, kPeriod);
  EXPECT_EQ(actual->geo_signal.latitude, kPos6.latitude);
  EXPECT_EQ(actual->geo_signal.longitude, kPos6.longitude);
  EXPECT_EQ(actual->geo_signal.timestamp, kTimestamp + kPeriod);
  ASSERT_TRUE(actual->geo_signal.direction);
  EXPECT_EQ(actual->geo_signal.direction->value(), 156.0);
  EXPECT_FALSE(actual->geo_signal.speed);
  EXPECT_FALSE(actual->geo_signal.accuracy);
}

TEST(PredictPosition, NoRouteTrackingTest) {
  {
    auto actual = GetRoutePredictedPosition(
        Route{}, {}, 0, std::chrono::system_clock::time_point{},
        std::chrono::seconds{10});
    EXPECT_FALSE(actual);
  }

  {
    auto actual = GetRoutePredictedPosition(
        Route{},
        {Eta{std::chrono::seconds{0}, 0 * ::geometry::meter,
             TrackingType::kUnknownDestination}},
        0, std::chrono::system_clock::time_point{}, std::chrono::seconds{10});
    EXPECT_FALSE(actual);
  }
}

TEST(PredictPosition, BeginOfRouteTest) {
  const Position kPos1{Lat{55.792159}, Lon{37.596296}};
  const Position kPos2{Lat{55.792569}, Lon{37.601796}};
  const Position kPos3{Lat{55.791009}, Lon{37.602013}};

  const Time kTime1{0};
  const Time kTime2{108};
  const Time kTime3{158};

  const Distance kDist1{0 * ::geometry::meter};
  const Distance kDist2{346 * ::geometry::meter};
  const Distance kDist3{508 * ::geometry::meter};

  const std::string kRouteId = "test_route_id";
  Route route;
  route.route_id = kRouteId;
  route.path = {{kPos1, kTime1, kDist1},
                {kPos1, kTime1, kDist1},
                {kPos2, kTime2, kDist2},
                {kPos3, kTime3, kDist3}};

  const Eta kEta = {std::chrono::seconds{158}, 508 * ::geometry::meter,
                    TrackingType::kRouteTracking};
  const size_t kSegmentIdx = 0;
  const std::chrono::system_clock::time_point kTimestamp{
      std::chrono::seconds{2134543}};
  const std::chrono::seconds kPeriod{0};

  auto actual = GetRoutePredictedPosition(route, {kEta}, kSegmentIdx,
                                          kTimestamp, kPeriod);

  ASSERT_TRUE(actual);
  EXPECT_EQ(actual->prediction_shift, kPeriod);
  EXPECT_EQ(actual->geo_signal.latitude.value(), kPos1.latitude.value());
  EXPECT_EQ(actual->geo_signal.longitude.value(), kPos1.longitude.value());
  EXPECT_EQ(actual->geo_signal.timestamp, kTimestamp + kPeriod);
  ASSERT_TRUE(actual->geo_signal.direction);
  EXPECT_EQ(actual->geo_signal.direction->value(), 82.0);
  EXPECT_FALSE(actual->geo_signal.speed);
  EXPECT_FALSE(actual->geo_signal.accuracy);
}

TEST(PredictPosition, CommonTest) {
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
                {kPos4, kTime4, kDist4}, {kPos5, kTime5, kDist5},
                {kPos5, kTime5, kDist5}, {kPos6, kTime6, kDist6}};

  const Eta kEta = {std::chrono::seconds{138}, 543 * ::geometry::meter,
                    TrackingType::kRouteTracking};
  const Eta kUnknownEta = {std::chrono::seconds{}, 0 * ::geometry::meter,
                           TrackingType::kUnknownDestination};
  const size_t kSegmentIdx = 2;
  const std::chrono::system_clock::time_point kTimestamp{
      std::chrono::seconds{2134543}};
  const std::chrono::seconds kPeriod{40};

  auto actual = GetRoutePredictedPosition(route, {kEta, kUnknownEta},
                                          kSegmentIdx, kTimestamp, kPeriod);
  auto expected = ::geometry::IntermediatePoint(
      kPos4, kPos5, (202.0 - 200.0) / (262.0 - 200.0));

  ASSERT_TRUE(actual);
  EXPECT_EQ(actual->prediction_shift, kPeriod);
  EXPECT_EQ(actual->geo_signal.latitude, expected.latitude);
  EXPECT_EQ(actual->geo_signal.longitude, expected.longitude);
  EXPECT_EQ(actual->geo_signal.timestamp, kTimestamp + kPeriod);
  EXPECT_EQ(actual->geo_signal.direction, Azimuth::from_value(246.0));
  EXPECT_FALSE(actual->geo_signal.speed);
  EXPECT_FALSE(actual->geo_signal.accuracy);
}
