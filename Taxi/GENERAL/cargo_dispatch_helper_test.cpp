#include "cargo_dispatch_helper.hpp"

#include <clients/cargo-dispatch/client.hpp>
#include <userver/formats/json.hpp>
#include <userver/utest/utest.hpp>

namespace {
using Response =
    clients::cargo_dispatch::v1_route_watch_info::post::Response200;
using OrderId = driver_route_responder::models::OrderId;
using PointId = driver_route_responder::models::PointId;
using Position = ::geometry::Position;
using Latitude = ::geometry::Latitude;
using Longitude = ::geometry::Longitude;
using RouterType = ::routing_base::RouterType;

const Position kDestination1{Longitude{10.0}, Latitude{20.0}};
const std::chrono::seconds kWaitTime1 = std::chrono::seconds{0};
const std::chrono::seconds kParkTime1 = std::chrono::seconds{0};
const OrderId kOrderId1{"order_id_1"};
const PointId kPointId1{"point_id_1"};

const Position kDestination2{Longitude{12.0}, Latitude{19.0}};
const std::chrono::seconds kWaitTime2 = std::chrono::seconds{240};
const std::chrono::seconds kParkTime2 = std::chrono::seconds{60};
const OrderId kOrderId2{"order_id_1"};
const PointId kPointId2{"point_id_2"};

const RouterType kRouterType = RouterType::kPedestrian;
const Position kPosition = Position{Longitude{16.0}, Latitude{9.0}};
const double kEtaMultiplier = 1.5;
const std::string kNearestZone = "Moscow";
const std::string kCountry = "Russia";
}  // namespace

TEST(CargoDispatchHelper, ParsingAllFieldsTest) {
  const std::string kValidResponse = R"json(
{
  "path": [
    {
      "point": [10.0, 20.0],
      "order_id": "order_id_1",
      "point_id": "point_id_1"
    },
    {
      "point": [12.0, 19.0],
      "order_id": "order_id_1",
      "point_id": "point_id_2",
      "wait_time": 240,
      "park_time": 60
    }
  ],
  "transport_type": "pedestrian",
  "performer_position": [16.0, 9.0],
  "eta_multiplier": 1.5,
  "nearest_zone": "Moscow",
  "country": "Russia"
})json";

  Response response = clients::cargo_dispatch::v1_route_watch_info::post::Parse(
      formats::json::FromString(kValidResponse),
      formats::parse::To<Response>{});

  auto actual =
      driver_route_responder::internal::FetchCargoDispatchRouteInfo(response);

  ASSERT_TRUE(actual.transport_type);
  EXPECT_EQ(*actual.transport_type, kRouterType);
  ASSERT_TRUE(actual.country);
  EXPECT_EQ(*actual.country, kCountry);
  ASSERT_TRUE(actual.nearest_zone);
  EXPECT_EQ(*actual.nearest_zone, kNearestZone);
  ASSERT_TRUE(actual.position);
  EXPECT_EQ(*actual.position, kPosition);
  EXPECT_EQ(actual.eta_multiplier, kEtaMultiplier);

  ASSERT_EQ(actual.points.size(), 2);
  EXPECT_EQ(actual.points[0].destination, kDestination1);
  EXPECT_EQ(actual.points[0].wait_time, kWaitTime1);
  EXPECT_EQ(actual.points[0].park_time, kParkTime1);
  EXPECT_EQ(actual.points[0].point_id, kPointId1);
  EXPECT_EQ(actual.points[0].order_id, kOrderId1);
  EXPECT_EQ(actual.points[1].destination, kDestination2);
  EXPECT_EQ(actual.points[1].wait_time, kWaitTime2);
  EXPECT_EQ(actual.points[1].park_time, kParkTime2);
  EXPECT_EQ(actual.points[1].point_id, kPointId2);
  EXPECT_EQ(actual.points[1].order_id, kOrderId2);
}

TEST(CargoDispatchHelper, ParsingOnlyRequiredFieldsTest) {
  const std::string kValidResponse = R"json(
{
  "path": [
    {
      "point": [10.0, 20.0],
      "order_id": "order_id_1",
      "point_id": "point_id_1"
    }
  ]
})json";

  Response response = clients::cargo_dispatch::v1_route_watch_info::post::Parse(
      formats::json::FromString(kValidResponse),
      formats::parse::To<Response>{});

  auto actual =
      driver_route_responder::internal::FetchCargoDispatchRouteInfo(response);

  ASSERT_FALSE(actual.transport_type);
  ASSERT_FALSE(actual.country);
  ASSERT_FALSE(actual.nearest_zone);
  ASSERT_FALSE(actual.position);
  EXPECT_EQ(actual.eta_multiplier, 1.0);

  ASSERT_EQ(actual.points.size(), 1);
  EXPECT_EQ(actual.points[0].destination, kDestination1);
  EXPECT_EQ(actual.points[0].wait_time, kWaitTime1);
  EXPECT_EQ(actual.points[0].park_time, kParkTime1);
  EXPECT_EQ(actual.points[0].point_id, kPointId1);
  EXPECT_EQ(actual.points[0].order_id, kOrderId1);
}

TEST(CargoDispatchHelper, FailedParsingTest) {
  const std::string kInvalidResponse = R"json(
{
  "path": [
    {
      "point": [10.0, 20.0]
    }
  ]
})json";

  Response response = clients::cargo_dispatch::v1_route_watch_info::post::Parse(
      formats::json::FromString(kInvalidResponse),
      formats::parse::To<Response>{});

  ASSERT_THROW(
      driver_route_responder::internal::FetchCargoDispatchRouteInfo(response),
      std::runtime_error);
}

TEST(CargoDispatchHelper, UnknownTransportTypeTest) {
  const std::string kInvalidResponse = R"json(
{
  "path": [
    {
      "point": [12.0, 19.0],
      "order_id": "order_id_1",
      "point_id": "point_id_2"
    }
  ],
  "transport_type": "unknown"
})json";

  Response response = clients::cargo_dispatch::v1_route_watch_info::post::Parse(
      formats::json::FromString(kInvalidResponse),
      formats::parse::To<Response>{});

  ASSERT_THROW(
      driver_route_responder::internal::FetchCargoDispatchRouteInfo(response),
      std::runtime_error);
}
