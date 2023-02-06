#include "order_core_helper.hpp"

#include <clients/order-core/client_gmock.hpp>
#include <userver/formats/json.hpp>

#include <userver/utest/utest.hpp>

TEST(OrderCoreHelper, ParsingTest) {
  const std::string kOrderId = "ads09sa092re09";
  const std::string kParentId = "dsajsaoijkqw3245d";

  const std::string kStatus = R"json({"order": {"status": "assigned"}})json";
  const std::string kFields = R"json(
{
  "performer": {
    "candidate_index": 0
  },
  "order": {
    "taxi_status": "driving",
    "request": {
      "destinations": [
        {
          "geopoint": [
            30.258271409001936,
            60.0065893755695
          ]
        }
      ],
      "source": {
        "geopoint": [
          30.33598143610203,
          59.98645481600687
        ],
        "country": "Russia"
      }
    },
    "status": "assigned",
    "calc": {
    },
    "nz": "spb",
    "user_phone_id": "assafd"
  },
  "_id": "ads09sa092re09",
  "candidates": [
    {
      "time": 253,
      "dist": 1800,
      "cp": {
        "id": "dsajsaoijkqw3245d",
        "dest": [
          30.334356959,
          59.986311887
        ]
      }
    }
  ],
  "order_info": {
    "statistics": {
      "status_updates": [
        {
          "c": "2021-09-15T09:07:32.006+00:00"
        },
        {
          "c": "2021-09-15T09:08:01.642+00:00"
        },
        {
          "c": "2021-09-15T09:08:32.782+00:00"
        },
        {
          "c": "2021-09-15T09:08:32.782+00:00",
          "t": "driving"
        }
      ]
    }
  }
})json";

  /// OrderCore response
  clients::order_core::v1_tc_order_fields::post::Response200 response_main;
  response_main.fields = {formats::json::FromString(kFields)};
  response_main.order_id = kOrderId;
  response_main.replica =
      clients::order_core::OrderFieldsResponseReplica::kMaster;
  response_main.version = "5";

  /// OrderCore response for checking driver status
  clients::order_core::v1_tc_order_fields::post::Response200 response_status;
  response_status.fields = {formats::json::FromString(kStatus)};
  response_status.order_id = kParentId;
  response_main.replica =
      clients::order_core::OrderFieldsResponseReplica::kMaster;
  response_main.version = "5";

  /// Order-core mock
  clients::order_core::ClientGMock mock_order_core;
  EXPECT_CALL(mock_order_core, V1TcOrderFields(testing::_, testing::_))
      .Times(2)
      .WillOnce(testing::Return(response_main))
      .WillOnce(testing::Return(response_status));

  /// Test's functionality
  auto request = driver_route_responder::internal::MakeOrderCoreRequest(
      mock_order_core, kOrderId);
  ASSERT_TRUE(request);
  auto order_core_info = driver_route_responder::internal::FetchOrderCoreInfo(
      kOrderId, *request, mock_order_core);

  driver_route_responder::internal::OrderCoreInfo expected;
  expected.parent_order_info = {kParentId,
                                {::geometry::Longitude(30.334356959),
                                 ::geometry::Latitude(59.986311887)}};
  expected.destinations = {{::geometry::Longitude(30.258271409001936),
                            ::geometry::Latitude(60.0065893755695)}};
  expected.order_status = "assigned";
  expected.taxi_status = "driving";
  expected.source = {::geometry::Longitude(30.33598143610203),
                     ::geometry::Latitude(59.98645481600687)};
  expected.driving_eta_distance = {1800 * ::geometry::meter};
  expected.driving_eta_time = std::chrono::seconds{253};
  expected.user_phone_id = "assafd";
  expected.order_zone = "spb";
  expected.country = "Russia";
  expected.use_toll_roads = false;
  expected.destinations_statuses = {};
  expected.last_status_info = {
      "driving", utils::datetime::Stringtime("2021-09-15T09:08:32.782+00:00",
                                             utils::datetime::kDefaultTimezone,
                                             utils::datetime::kRfc3339Format)};

  ASSERT_TRUE(order_core_info.parent_order_info);
  EXPECT_EQ(order_core_info.parent_order_info->order_id,
            expected.parent_order_info->order_id);
  EXPECT_EQ(order_core_info.parent_order_info->destination,
            expected.parent_order_info->destination);
  EXPECT_EQ(order_core_info.order_zone, expected.order_zone);
  EXPECT_EQ(order_core_info.user_phone_id, expected.user_phone_id);
  EXPECT_EQ(order_core_info.driving_eta_time, expected.driving_eta_time);
  EXPECT_EQ(order_core_info.driving_eta_distance,
            expected.driving_eta_distance);
  EXPECT_EQ(order_core_info.calc_alternative_type,
            expected.calc_alternative_type);
  EXPECT_EQ(order_core_info.destinations, expected.destinations);
  EXPECT_EQ(order_core_info.order_status, expected.order_status);
  EXPECT_EQ(order_core_info.taxi_status, expected.taxi_status);
  EXPECT_EQ(order_core_info.source, expected.source);
  EXPECT_EQ(order_core_info.use_toll_roads, expected.use_toll_roads);
  ASSERT_TRUE(order_core_info.last_status_info.has_value());
  EXPECT_EQ(order_core_info.last_status_info->last_taxi_status,
            expected.last_status_info->last_taxi_status);
  EXPECT_EQ(order_core_info.last_status_info->update_time,
            expected.last_status_info->update_time);
}
