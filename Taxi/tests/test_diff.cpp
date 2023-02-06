#include <gtest/gtest.h>

#include <userver/formats/json.hpp>
#include <views/dump_differ.hpp>

TEST(TestDiff, TestDriversDiff) {
  std::string dump1 = R"(
    {
      "date":"2019-03-05T14:59",
      "drivers":[
        {
          "driver_uuid": "5c1ea76eaa0342ae89b49d0d69cc50c3",
          "id": "643753730233_5c1ea76eaa0342ae89b49d0d69cc50c3",
          "is_econom": true,
          "park_id": "7f74df331eb04ad78bc2ff25ff88a8f2",
          "zone": "moscow",
          "payment_methods":[
             "applepay",
             "card",
             "cash",
             "coupon",
             "googlepay",
             "personal_wallet"]
        },
        {
          "driver_uuid": "78acdd7ebb1946429ed26c4b6efb7232",
          "id": "643753730233_78acdd7ebb1946429ed26c4b6efb7232",
          "is_econom": true,
          "zone": "moscow",
          "park_id": "7f74df331eb04ad78bc2ff25ff88a8f2",
          "payment_methods":[
             "applepay",
             "card",
             "cash",
             "coupon",
             "googlepay",
             "personal_wallet"]
        }
      ]
    })";
  std::string dump2 = R"(
    {
      "date":"2019-03-05T15:59",
      "drivers":[
        {
          "driver_uuid": "5c1ea76eaa0342ae89b49d0d69cc50c2",
          "id": "643753730233_5c1ea76eaa0342ae89b49d0d69cc50c2",
          "is_econom":true,
          "park_id": "7f74df331eb04ad78bc2ff25ff88a8f2",
          "zone": "moscow",
          "payment_methods":[
             "applepay",
             "card",
             "cash",
             "coupon",
             "googlepay",
             "personal_wallet"]
        },
        {
          "driver_uuid": "78acdd7ebb1946429ed26c4b6efb7232",
          "id": "643753730233_78acdd7ebb1946429ed26c4b6efb7232",
          "is_econom":false,
          "park_id":"7f74df331eb04ad78bc2ff25ff88a8f2",
          "zone": "moscow",
          "payment_methods":[
             "applepay",
             "super_card",
             "cash",
             "coupon",
             "googlepay",
             "personal_wallet"]
        }
      ]})";
  auto dump1_json = formats::json::FromString(dump1);
  auto dump2_json = formats::json::FromString(dump2);
  auto diff = supply_diagnostics::views::GetDriversDumpsDiff(
      dump1_json, dump2_json, "moscow");
  EXPECT_EQ("2019-03-05T14:59", diff["first_date"].As<std::string>())
      << formats::json::ToString(diff);
  EXPECT_EQ("2019-03-05T15:59", diff["second_date"].As<std::string>())
      << formats::json::ToString(diff);
  EXPECT_EQ(1, diff["cant_econom"].GetSize()) << formats::json::ToString(diff);
  EXPECT_EQ(1, diff["new_drivers"]["moscow"].GetSize())
      << formats::json::ToString(diff);
  EXPECT_EQ(1, diff["removed_drivers"]["moscow"].GetSize())
      << formats::json::ToString(diff);
  EXPECT_EQ(1, diff["payment_method_added"]["super_card"].GetSize())
      << formats::json::ToString(diff);
  EXPECT_EQ(1, diff["payment_method_removed"]["card"].GetSize())
      << formats::json::ToString(diff);
}
