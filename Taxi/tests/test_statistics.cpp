#include <gtest/gtest.h>

#include <userver/formats/json.hpp>

#include <models/driver_data.hpp>
#include <models/driver_statistics.hpp>
#include <utils/statistics_storage.hpp>

TEST(TestDriversStatistics, TestCount) {
  std::string driver1 = R"(
      {
        "allowed_payment_methods": [
          "card",
          "applepay",
          "googlepay",
          "coupon"
        ],
        "car_classes": [],
        "geopoint": [
          37.503288999999995,
          55.659450999999997
        ],
        "driver_status": "free",
        "tx_status": "free",
        "driver_id": "643753730233_359e817230a24501ad627845b078dc5a",
        "driver_uuid": "359e817230a24501ad627845b078dc5a",
        "park_db_id": "7f74df331eb04ad78bc2ff25ff88a8f1"})";
  std::string driver2 = R"(
      {
        "allowed_payment_methods": [
          "cash",
          "applepay",
          "googlepay",
          "coupon"
        ],
        "car_classes": ["econom", "pool", "uberblack"],
        "geopoint": [
          37.503288999999995,
          55.659450999999997
        ],
        "driver_status": "free",
        "tx_status": "free",
        "driver_id": "643753730233_359e817230a24501ad627845b078dc5b",
        "driver_uuid": "359e817230a24501ad627845b078dc5b",
        "park_db_id": "7f74df331eb04ad78bc2ff25ff88a8f2"})";
  std::string driver3 = R"(
      {
        "allowed_payment_methods": [
          "cash",
          "card",
          "googlepay",
          "coupon"],
        "car_classes": ["pool", "uberblack"],
        "geopoint": [
          37.503288999999995,
          55.659450999999997 ],
        "driver_status": "free",
        "tx_status": "free",
        "driver_id": "643753730233_359e817230a24501ad627845b078dc5c",
        "driver_uuid": "359e817230a24501ad627845b078dc5c",
        "park_db_id": "7f74df331eb04ad78bc2ff25ff88a8f3"})";

  supply_diagnostics::models::DriverStatistics statistics;
  auto json = formats::json::FromString(driver1);
  auto driver = supply_diagnostics::models::DriverData(json);
  driver.zone = "moscow";
  statistics.AddStatistics(driver);

  json = formats::json::FromString(driver2);
  driver = supply_diagnostics::models::DriverData(json);
  driver.zone = "moscow";
  statistics.AddStatistics(driver);

  json = formats::json::FromString(driver3);
  driver = supply_diagnostics::models::DriverData(json);
  driver.zone = "moscow";
  statistics.AddStatistics(driver);
  json = statistics.ToJson();

  EXPECT_EQ(json["count"].As<std::size_t>(), 3)
      << formats::json::ToString(json);
  EXPECT_EQ(json["econom"].As<std::size_t>(), 1)
      << formats::json::ToString(json);
  EXPECT_EQ(json["payment_methods"]["cash"].As<std::size_t>(), 2);
  EXPECT_EQ(json["payment_methods"]["card"].As<std::size_t>(), 2);
  EXPECT_EQ(json["payment_methods"]["applepay"].As<std::size_t>(), 2);
  EXPECT_EQ(json["payment_methods"]["googlepay"].As<std::size_t>(), 3);
  EXPECT_EQ(json["payment_methods"]["coupon"].As<std::size_t>(), 3);
  EXPECT_EQ(json["moscow"]["payment_methods"]["cash"].As<std::size_t>(), 2);
  EXPECT_EQ(json["moscow"]["payment_methods"]["card"].As<std::size_t>(), 2);
  EXPECT_EQ(json["moscow"]["payment_methods"]["applepay"].As<std::size_t>(), 2);
  EXPECT_EQ(json["moscow"]["payment_methods"]["googlepay"].As<std::size_t>(),
            3);
  EXPECT_EQ(json["moscow"]["payment_methods"]["coupon"].As<std::size_t>(), 3);
}

TEST(TestStatisticsStorage, TestToJson) {
  supply_diagnostics::utils::StatisticsStorage storage;
  storage.UpdateMetric("test_node.test_value", 1);
  storage.UpdateMetric("test_node.test_metric", 1);
  storage.UpdateMetric("test_node2.test_metric", 1);
  storage.UpdateMetric("test_metric", 3);
  auto json = storage.ToJson().ExtractValue();
  ASSERT_EQ(1, json["test_node"]["test_value"].As<int>());
  ASSERT_EQ(1, json["test_node"]["test_metric"].As<int>());
  ASSERT_EQ(1, json["test_node2"]["test_metric"].As<int>());
  ASSERT_EQ(3, json["test_metric"].As<int>());
}
