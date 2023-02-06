#include <gtest/gtest.h>

#include <userver/formats/bson/serialize.hpp>
#include <userver/formats/json.hpp>

#include <models/driver_data.hpp>
#include <models/geo_zone.hpp>
#include <models/park_activation.hpp>
#include <models/park_data.hpp>

TEST(TestDriverData, TestParseFromString) {
  std::string data = R"(
  {
    "allowed_payment_methods": [
        "cash",
        "card",
        "applepay",
        "googlepay",
        "coupon",
        "personal_wallet"
    ],
    "geopoint": [
        37.503288999999995,
        55.659450999999997
    ],
    "driver_status": "free",
    "tx_status" : "free",
    "car_classes": [
        "econom",
        "pool",
        "uberx",
        "uberselect",
        "uberblack",
        "uberstart",
        "start",
        "standart",
        "selfdriving",
        "ubervan",
        "uberlux",
        "uberselectplus",
        "maybach"
    ],
    "driver_id": "643753730233_359e817230a24501ad627845b078dc5e",
    "driver_uuid": "359e817230a24501ad627845b078dc5e",
    "park_db_id": "7f74df331eb04ad78bc2ff25ff88a8f2"
  }
  )";

  auto json = formats::json::FromString(data);
  supply_diagnostics::models::DriverData driver{json};
  ASSERT_EQ(driver.id, "643753730233_359e817230a24501ad627845b078dc5e");
  ASSERT_EQ(driver.uuid, "359e817230a24501ad627845b078dc5e");
  ASSERT_EQ(driver.park_id, "7f74df331eb04ad78bc2ff25ff88a8f2");
  ASSERT_TRUE(driver.is_econom);
}

TEST(TestGeoZone, TestModelParsing) {
  std::string data = R"(
  {
    "removed": true,
    "name": "novorossiysk",
    "area": 0.030135313159000893,
    "geometry":
     {
       "type": "Polygon",
       "coordinates": [
          [[37.55, 44.6],
           [37.5, 44.55],
           [37.55, 44.5],
           [37.6, 44.55]]]
     },
     "_id": "0d288c3f16d04e298ed7a850a5ce5752",
     "geo_id": 150
  }
  )";

  auto geozone = formats::bson::FromJsonString(data)
                     .As<supply_diagnostics::models::GeoZone>();
  ASSERT_EQ(37.6, geozone.top);
  ASSERT_EQ(44.5, geozone.left);
  ASSERT_EQ(37.5, geozone.bottom);
  ASSERT_EQ(44.6, geozone.right);
}

TEST(TestGeoZone, TestCheckInside) {
  std::string data = R"(
  {
    "removed": true,
    "name": "test_zone",
    "area": 0.030135313159000893,
    "geometry":
     {
       "type": "Polygon",
       "coordinates": [
          [[37.55, 44.6],
           [37.5, 44.55],
           [37.55, 44.5],
           [37.6, 44.55]]]
     },
     "_id": "0d288c3f16d04e298ed7a850a5ce5752",
     "geo_id": 150
  }
  )";

  auto geozone = formats::bson::FromJsonString(data)
                     .As<supply_diagnostics::models::GeoZone>();
  ASSERT_FALSE(std::abs(geozone.DistanceTo(std::make_pair(55, 37))) <=
               std::numeric_limits<double>::epsilon());
  ASSERT_DOUBLE_EQ(geozone.DistanceTo(std::make_pair(37.55, 44.55)), 0);
  ASSERT_FALSE(std::abs(geozone.DistanceTo(std::make_pair(37.4, 44.55))) <=
               std::numeric_limits<double>::epsilon());
}

TEST(TestGeoZone, TestCheckInsideComplex) {
  std::string data = R"(
  {
    "removed": true,
    "name": "test_zone",
    "area": 0.030135313159000893,
    "geometry":
     {
       "type": "Polygon",
       "coordinates": [
          [[0.0, 0.0],
           [0.0, 10.0],
           [10.0, 15.0],
           [20.0, 10.0],
           [20.0, 0.0],
           [15.0, 0.0],
           [15.0, 8.0],
           [5.0, 8.0],
           [5.0, 0.0]]]
     },
     "_id": "0d288c3f16d04e298ed7a850a5ce5752",
     "geo_id": 150
  }
  )";

  auto geozone = formats::bson::FromJsonString(data)
                     .As<supply_diagnostics::models::GeoZone>();
  ASSERT_DOUBLE_EQ(geozone.DistanceTo(std::make_pair(4.0, 4.0)), 0);
  ASSERT_DOUBLE_EQ(geozone.DistanceTo(std::make_pair(10.0, 10.0)), 0);
  ASSERT_FALSE(geozone.DistanceTo(std::make_pair(10.0, 5.0)) <= 0);
  ASSERT_FALSE(geozone.DistanceTo(std::make_pair(0.0, 11.0)) <= 0);
}

TEST(TestParksData, TestsParse) {
  std::string data = R"(
  {
    "_id": "clid0",
    "city": "Москва",
    "name": "Я.Taxi",
    "host": "host",
    "takes_urgent": true,
    "requirements": {
      "creditcard": true
    },
    "account": {
        "contracts": [{
            "is_of_cash": true,
            "is_of_card": true,
            "services": [111, 128],
            "currency": "RUB"
        }]
    },
    "updated_ts": {
      "$timestamp": {
        "t": 0,
        "i": 0
      }
    }
  })";
  auto bson = formats::bson::FromJsonString(data);
  auto park = bson.As<supply_diagnostics::models::ParkData>();
  ASSERT_TRUE(park.can_cash);
  ASSERT_TRUE(park.can_card);
  ASSERT_FALSE(park.can_corp);
}
