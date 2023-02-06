#include "cargo_fallback.hpp"

#include <userver/utest/utest.hpp>

namespace {
using Reasons =
    driver_route_responder::internal::cargo::different_points::Reasons;
using CargoPoint = driver_route_responder::internal::CargoPoint;
using CargoDispatchRouteInfo =
    driver_route_responder::internal::CargoDispatchRouteInfo;
using OrderId = driver_route_responder::models::OrderId;
using PointId = driver_route_responder::models::PointId;
using Timelefts = driver_route_responder::models::InternalTimelefts;
using TimeleftData = driver_route_responder::models::InternalTimeleftData;
using Route = driver_route_responder::models::Route;
using RouteInfo = driver_route_responder::models::RouteInfo;
using TrackstoryPosition = driver_route_responder::internal::Position;
using TrackingType = ::geobus::types::TrackingType;
using Distance = ::geometry::Distance;
using Position = ::geometry::Position;
using Latitude = ::geometry::Latitude;
using Longitude = ::geometry::Longitude;
using RouterType = routing_base::RouterType;

const Position kDestination1{Longitude{10.0}, Latitude{20.0}};
const std::chrono::seconds kWaitTime1 = std::chrono::seconds{0};
const std::chrono::seconds kParkTime1 = std::chrono::seconds{0};
const OrderId kOrderId1{"order_id_1"};
const OrderId kOtherOrderId1{"order_id_1_other"};
const PointId kPointId1{"point_id_1"};

const Position kDestination2{Longitude{12.0}, Latitude{19.0}};
const Position kOtherDestination2{Longitude{37.0}, Latitude{89.0}};
const std::chrono::seconds kWaitTime2 = std::chrono::seconds{240};
const std::chrono::seconds kParkTime2 = std::chrono::seconds{60};
const OrderId kOrderId2{"order_id_1"};
const PointId kPointId2{"point_id_2"};
const PointId kOtherPointId2{"point_id_2_other"};

const RouterType kRouterType = RouterType::kPedestrian;
const Position kPosition = Position{Longitude{16.0}, Latitude{9.0}};
const double kEtaMultiplier = 1.5;
const std::string kNearestZone = "Moscow";
const std::string kCountry = "Russia";

const std::chrono::seconds kRouteTime1{600};
const Distance kRouteDistance1{8567 * ::geometry::meter};
const std::chrono::seconds kRouteTime2{2100};
const Distance kRouteDistance2{23851 * ::geometry::meter};
const ::gpssignal::GpsSignal kGpsSignal{
    Latitude{57.0},
    Longitude{24.0},
    std::nullopt,
    std::nullopt,
    std::nullopt,
    std::chrono::system_clock::time_point{
        std::chrono::milliseconds{875245134255}}};
const TrackstoryPosition kTrackstoryPosition =
    TrackstoryPosition{kGpsSignal, RouterType::kMasstransit};
const std::string kCargoDispatchStr = "cargo-dispatch";

// time1 = 600 * eta_multiplier + park_time1
// time2 = 2100 * eta_multiplier + park_time1 + wait_time1 + park_time2
const std::chrono::seconds kTime1 =
    std::chrono::duration_cast<std::chrono::seconds>(kRouteTime1 *
                                                     kEtaMultiplier) +
    kParkTime1;
const std::chrono::seconds kTime2 =
    std::chrono::duration_cast<std::chrono::seconds>(kRouteTime2 *
                                                     kEtaMultiplier) +
    kParkTime1 + kWaitTime1 + kParkTime2;

std::tuple<Timelefts, CargoDispatchRouteInfo>
MakeEqualTimeleftsAndVerificationData() {
  CargoDispatchRouteInfo verification_data;

  verification_data.eta_multiplier = kEtaMultiplier;
  verification_data.position = kPosition;
  verification_data.nearest_zone = kNearestZone;
  verification_data.country = kCountry;
  verification_data.transport_type = kRouterType;

  verification_data.points.resize(2);
  verification_data.points[0].point_id = kPointId1;
  verification_data.points[0].order_id = kOrderId1;
  verification_data.points[0].park_time = kParkTime1;
  verification_data.points[0].wait_time = kWaitTime1;
  verification_data.points[0].destination = kDestination1;
  verification_data.points[1].point_id = kPointId2;
  verification_data.points[1].order_id = kOrderId2;
  verification_data.points[1].park_time = kParkTime2;
  verification_data.points[1].wait_time = kWaitTime2;
  verification_data.points[1].destination = kDestination2;

  Timelefts timelefts;
  timelefts.timestamp = kGpsSignal.timestamp;
  timelefts.raw_pos = kGpsSignal;
  timelefts.tracking_type = TrackingType::kRouteTracking;

  timelefts.timeleft_data.resize(2);
  timelefts.timeleft_data[0].order_id = kOrderId1.GetUnderlying();
  timelefts.timeleft_data[0].point_id = kPointId1.GetUnderlying();
  timelefts.timeleft_data[0].destination_position = kDestination1;
  timelefts.timeleft_data[0].service_id = kCargoDispatchStr;
  timelefts.timeleft_data[0].time_distance_left = {kTime1, kRouteDistance1};
  timelefts.timeleft_data[0].raw_time_distance_left = {kTime1, kRouteDistance1};
  timelefts.timeleft_data[1].order_id = kOrderId2.GetUnderlying();
  timelefts.timeleft_data[1].point_id = kPointId2.GetUnderlying();
  timelefts.timeleft_data[1].destination_position = kDestination2;
  timelefts.timeleft_data[1].service_id = kCargoDispatchStr;
  timelefts.timeleft_data[1].time_distance_left = {kTime2, kRouteDistance2};
  timelefts.timeleft_data[1].raw_time_distance_left = {kTime2, kRouteDistance2};

  return {timelefts, verification_data};
}

}  // namespace

TEST(CargoFallback, ComarisionEmptyVerificationPathTest) {
  CargoDispatchRouteInfo verification_data;

  auto [is_equal, reason] = driver_route_responder::internal::Compare(
      std::nullopt, verification_data);

  EXPECT_FALSE(is_equal);
  EXPECT_EQ(reason, Reasons::kEmptyVerificationPath);
}

TEST(CargoFallback, ComarisionEmptyTimeleftsTest) {
  CargoDispatchRouteInfo verification_data;
  verification_data.points = {CargoPoint{}};

  auto [is_equal, reason] = driver_route_responder::internal::Compare(
      std::nullopt, verification_data);

  EXPECT_FALSE(is_equal);
  EXPECT_EQ(reason, Reasons::kNoTimelefts);
}

TEST(CargoFallback, ComparisionDifferentPointIdTest) {
  auto [timelefts, verification_data] = MakeEqualTimeleftsAndVerificationData();

  verification_data.points[1].point_id = kOtherPointId2;

  auto [is_equal, reason] =
      driver_route_responder::internal::Compare(timelefts, verification_data);

  EXPECT_FALSE(is_equal);
  EXPECT_EQ(reason, Reasons::kDifferentPointId);
}

TEST(CargoFallback, ComparisionDifferentOrderIdTest) {
  auto [timelefts, verification_data] = MakeEqualTimeleftsAndVerificationData();

  verification_data.points[0].order_id = kOtherOrderId1;

  auto [is_equal, reason] =
      driver_route_responder::internal::Compare(timelefts, verification_data);

  EXPECT_FALSE(is_equal);
  EXPECT_EQ(reason, Reasons::kDifferentOrderId);
}

TEST(CargoFallback, ComparisionDifferentSizesTest) {
  auto [timelefts, verification_data] = MakeEqualTimeleftsAndVerificationData();

  timelefts.timeleft_data.resize(1);

  auto [is_equal, reason] =
      driver_route_responder::internal::Compare(timelefts, verification_data);

  EXPECT_FALSE(is_equal);
  EXPECT_EQ(reason, Reasons::kDifferentSizes);
}

TEST(CargoFallback, ComparisionDifferentDestinationPositionTest) {
  auto [timelefts, verification_data] = MakeEqualTimeleftsAndVerificationData();

  verification_data.points[1].destination = kOtherDestination2;

  auto [is_equal, reason] =
      driver_route_responder::internal::Compare(timelefts, verification_data);

  EXPECT_FALSE(is_equal);
  EXPECT_EQ(reason, Reasons::kDifferentDestinationPosition);
}

TEST(CargoFallback, ComparisionBaseTest) {
  auto [timelefts, verification_data] = MakeEqualTimeleftsAndVerificationData();

  auto [is_equal, reason] =
      driver_route_responder::internal::Compare(timelefts, verification_data);

  EXPECT_TRUE(is_equal);
  EXPECT_EQ(reason, Reasons::kEqual);
}

TEST(CargoFallback, MakeCargoInternalTimeleftsFromInfos) {
  auto [expected, verification_data] = MakeEqualTimeleftsAndVerificationData();

  expected.from_fallback = true;
  expected.fallback_reason =
      driver_route_responder::internal::cargo::different_points::ToString(
          Reasons::kNoTimelefts);

  RouteInfo route_info_1;
  route_info_1.distance = kRouteDistance1;
  route_info_1.time = kRouteTime1;
  RouteInfo route_info_2;
  route_info_2.distance = kRouteDistance2;
  route_info_2.time = kRouteTime2;

  auto actual = driver_route_responder::internal::MakeCargoInternalTimelefts(
      {route_info_1, route_info_2}, verification_data, kTrackstoryPosition,
      Reasons::kNoTimelefts);

  ASSERT_EQ(expected.timeleft_data.size(), actual.timeleft_data.size());
  for (size_t i = 0; i < expected.timeleft_data.size(); ++i) {
    EXPECT_EQ(expected.timeleft_data[i].order_id,
              actual.timeleft_data[i].order_id);
    EXPECT_EQ(expected.timeleft_data[i].point_id,
              actual.timeleft_data[i].point_id);
    EXPECT_EQ(expected.timeleft_data[i].service_id,
              actual.timeleft_data[i].service_id);
    EXPECT_EQ(expected.timeleft_data[i].destination_position,
              actual.timeleft_data[i].destination_position);
    ASSERT_TRUE(expected.timeleft_data[i].time_distance_left);
    ASSERT_TRUE(actual.timeleft_data[i].time_distance_left);
    EXPECT_EQ(expected.timeleft_data[i].time_distance_left->time,
              actual.timeleft_data[i].time_distance_left->time);
    EXPECT_EQ(expected.timeleft_data[i].time_distance_left->distance,
              actual.timeleft_data[i].time_distance_left->distance);
    ASSERT_TRUE(expected.timeleft_data[i].raw_time_distance_left);
    ASSERT_TRUE(actual.timeleft_data[i].raw_time_distance_left);
    EXPECT_EQ(expected.timeleft_data[i].raw_time_distance_left->time,
              actual.timeleft_data[i].raw_time_distance_left->time);
    EXPECT_EQ(expected.timeleft_data[i].raw_time_distance_left->distance,
              actual.timeleft_data[i].raw_time_distance_left->distance);
  }
  EXPECT_EQ(expected.from_fallback, actual.from_fallback);
  EXPECT_EQ(expected.raw_pos, actual.raw_pos);
  EXPECT_EQ(expected.fallback_reason, actual.fallback_reason);
  EXPECT_EQ(expected.tracking_type, actual.tracking_type);
  EXPECT_EQ(expected.timestamp, actual.timestamp);
}

TEST(CargoFallback, MakeCargoInternalTimeleftsFromRoute) {
  const std::string kRouteId = "route_id";

  auto [expected, verification_data] = MakeEqualTimeleftsAndVerificationData();

  expected.raw_pos =
      gpssignal::GpsSignal{kPosition.latitude, kPosition.longitude};
  expected.route_id = kRouteId;

  Route route;
  route.route_id = kRouteId;
  route.info.time = kRouteTime2;
  route.info.distance = kRouteDistance2;
  route.legs = {{0}, {1}};
  route.path.push_back(clients::routing::RoutePoint{kPosition});
  route.path.push_back({kDestination1, kRouteTime1, kRouteDistance1});
  route.path.push_back({kDestination2, kRouteTime2, kRouteDistance2});

  auto actual = driver_route_responder::internal::MakeCargoInternalTimelefts(
      route, verification_data, std::nullopt, std::nullopt);

  ASSERT_EQ(expected.timeleft_data.size(), actual.timeleft_data.size());
  for (size_t i = 0; i < expected.timeleft_data.size(); ++i) {
    EXPECT_EQ(expected.timeleft_data[i].order_id,
              actual.timeleft_data[i].order_id);
    EXPECT_EQ(expected.timeleft_data[i].point_id,
              actual.timeleft_data[i].point_id);
    EXPECT_EQ(expected.timeleft_data[i].service_id,
              actual.timeleft_data[i].service_id);
    EXPECT_EQ(expected.timeleft_data[i].destination_position,
              actual.timeleft_data[i].destination_position);
    ASSERT_TRUE(expected.timeleft_data[i].time_distance_left);
    ASSERT_TRUE(actual.timeleft_data[i].time_distance_left);
    EXPECT_EQ(expected.timeleft_data[i].time_distance_left->time,
              actual.timeleft_data[i].time_distance_left->time);
    EXPECT_EQ(expected.timeleft_data[i].time_distance_left->distance,
              actual.timeleft_data[i].time_distance_left->distance);
    ASSERT_TRUE(expected.timeleft_data[i].raw_time_distance_left);
    ASSERT_TRUE(actual.timeleft_data[i].raw_time_distance_left);
    EXPECT_EQ(expected.timeleft_data[i].raw_time_distance_left->time,
              actual.timeleft_data[i].raw_time_distance_left->time);
    EXPECT_EQ(expected.timeleft_data[i].raw_time_distance_left->distance,
              actual.timeleft_data[i].raw_time_distance_left->distance);
  }
  EXPECT_EQ(expected.from_fallback, actual.from_fallback);
  EXPECT_EQ(expected.raw_pos, actual.raw_pos);
  EXPECT_EQ(expected.fallback_reason, actual.fallback_reason);
  EXPECT_EQ(expected.tracking_type, actual.tracking_type);
  EXPECT_EQ(expected.route_id, actual.route_id);
  EXPECT_EQ(actual.route_id, kRouteId);
  ASSERT_TRUE(actual.route);
  EXPECT_EQ(actual.route->size(), route.path.size());
}
