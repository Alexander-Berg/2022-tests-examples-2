#include "common_filter.hpp"

#include <userver/utest/utest.hpp>

#include <defs/api/api.hpp>
#include <defs/definitions.hpp>

namespace models::fleet_map {

TEST(CommonFilterTest, TestSearchType) {
  handlers::DriversCommonRequest body;
  body.search = "super";
  auto filter = CommonFilter(body);
  EXPECT_EQ(filter.GetType(), CommonFilterType::kSearch);
  EXPECT_EQ(filter.GetSearch(), "super");
  EXPECT_THROW(filter.GetPreset(), std::runtime_error);
  EXPECT_EQ(filter.GetPaymentMethods().size(), 0);
  EXPECT_EQ(filter.GetStatuses().size(), 0);
}

TEST(CommonFilterTest, TestPresetType_OnlyCash) {
  handlers::DriversCommonRequest body;
  body.preset = handlers::DriversPreset::kPaymentMethodOnlyCash;
  auto filter = CommonFilter(body);
  EXPECT_EQ(filter.GetType(), CommonFilterType::kPreset);
  EXPECT_THROW(filter.GetSearch(), std::runtime_error);
}

TEST(CommonFilterTest, TestPresetType_StatusFree) {
  handlers::DriversCommonRequest body;
  body.preset = handlers::DriversPreset::kStatusFree;
  auto filter = CommonFilter(body);
  EXPECT_EQ(filter.GetType(), CommonFilterType::kPreset);
  EXPECT_EQ(filter.GetStatuses().size(), 1);
  EXPECT_EQ(filter.GetStatuses()[0], handlers::DriverStatus::kFree);
  EXPECT_EQ(filter.GetPaymentMethods().size(), 0);
}

TEST(CommonFilterTest, TestFilterType_EmptyFilter) {
  auto filter = CommonFilter(handlers::DriversCommonRequest{});
  EXPECT_EQ(filter.GetType(), CommonFilterType::kFilter);
  EXPECT_THROW(filter.GetPreset(), std::runtime_error);
  EXPECT_THROW(filter.GetSearch(), std::runtime_error);
}

TEST(CommonFilterTest, TestFilterType_FullFilter) {
  auto filter =
      CommonFilter(handlers::DriversCommonRequest{handlers::DriversFilter{
          std::unordered_set<handlers::DriverPaymentMethod>{
              handlers::DriverPaymentMethod::kCash},
          std::unordered_set<handlers::DriverStatus>{
              handlers::DriverStatus::kFree, handlers::DriverStatus::kInOrder},
          std::unordered_set<std::string>{"work_rule_id1", "work_rule_id2"},
      }});
  EXPECT_EQ(filter.GetType(), CommonFilterType::kFilter);
  EXPECT_EQ(filter.GetPaymentMethods().size(), 1);
  EXPECT_EQ(filter.GetStatuses().size(), 2);
  EXPECT_EQ(filter.GetWorkRuleIds().size(), 2);
}

}  // namespace models::fleet_map
