#include <gmock/gmock.h>

#include <models/tracking_data.hpp>

namespace {
using eats_orders_tracking::models::TrackingWaybill;
}  // namespace

TEST(WaybillFilter, NoActiveWaybills) {
  std::vector<TrackingWaybill> waybills;
  waybills.resize(2);
  waybills[0].waybill_ref = "w1";
  waybills[0].waybill_resolution = "failed";
  waybills[1].waybill_ref = "w2";
  waybills[1].waybill_resolution = "replaced";
  std::string order_nr = "111111-111111";
  auto actual_result =
      eats_orders_tracking::models::FilterWaybills(order_nr, waybills);
  ASSERT_FALSE(actual_result.has_value());
}

TEST(WaybillFilter, ActualWaybill) {
  std::vector<TrackingWaybill> waybills;
  waybills.resize(2);
  waybills[1].waybill_ref = "w1";
  waybills[1].is_actual_waybill = false;
  waybills[0].waybill_ref = "w2";
  waybills[0].is_actual_waybill = true;
  std::string order_nr = "111111-111111";
  std::string expected_waybill_ref = "w2";
  auto actual_result =
      eats_orders_tracking::models::FilterWaybills(order_nr, waybills);
  ASSERT_TRUE(actual_result.has_value());
  ASSERT_EQ(actual_result->waybill_ref, expected_waybill_ref);
}

TEST(WaybillFilter, CargoWaybillCreatedAt) {
  std::vector<TrackingWaybill> waybills;
  waybills.resize(2);
  waybills[1].waybill_ref = "w1";
  waybills[1].cargo_waybill_created_at = storages::postgres::TimePointTz{
      utils::datetime::Stringtime("2020-01-01T00:00:00.00Z", "UTC")};
  waybills[0].waybill_ref = "w2";
  waybills[0].cargo_waybill_created_at = storages::postgres::TimePointTz{
      utils::datetime::Stringtime("2020-01-01T00:00:01.00Z", "UTC")};
  std::string order_nr = "111111-111111";
  std::string expected_waybill_ref = "w2";
  auto actual_result =
      eats_orders_tracking::models::FilterWaybills(order_nr, waybills);
  ASSERT_TRUE(actual_result.has_value());
  ASSERT_EQ(actual_result->waybill_ref, expected_waybill_ref);
}

TEST(WaybillFilter, OptionalCargoWaybillCreatedAt) {
  std::vector<TrackingWaybill> waybills;
  waybills.resize(2);
  waybills[1].waybill_ref = "w1";
  waybills[1].cargo_waybill_created_at = std::nullopt;
  waybills[0].waybill_ref = "w2";
  waybills[0].cargo_waybill_created_at = storages::postgres::TimePointTz{
      utils::datetime::Stringtime("2020-01-01T00:00:01.00Z", "UTC")};
  std::string order_nr = "111111-111111";
  std::string expected_waybill_ref = "w2";
  auto actual_result =
      eats_orders_tracking::models::FilterWaybills(order_nr, waybills);
  ASSERT_TRUE(actual_result.has_value());
  ASSERT_EQ(actual_result->waybill_ref, expected_waybill_ref);
}

TEST(WaybillFilter, CreatedAt) {
  std::vector<TrackingWaybill> waybills;
  waybills.resize(2);
  waybills[1].waybill_ref = "w1";
  waybills[1].created_at = storages::postgres::TimePointTz{
      utils::datetime::Stringtime("2020-01-01T00:00:00.00Z", "UTC")};
  waybills[0].waybill_ref = "w2";
  waybills[0].created_at = storages::postgres::TimePointTz{
      utils::datetime::Stringtime("2020-01-01T00:00:01.00Z", "UTC")};
  std::string order_nr = "111111-111111";
  std::string expected_waybill_ref = "w2";
  auto actual_result =
      eats_orders_tracking::models::FilterWaybills(order_nr, waybills);
  ASSERT_TRUE(actual_result.has_value());
  ASSERT_EQ(actual_result->waybill_ref, expected_waybill_ref);
}
