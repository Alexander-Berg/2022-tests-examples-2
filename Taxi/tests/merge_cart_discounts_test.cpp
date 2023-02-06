#include <gtest/gtest.h>

#include <clients/eats-discounts/definitions.hpp>

#include <applicators/cart_applier.hpp>
#include <eats-discounts-applicator/common.hpp>
#include <experiments3.hpp>
#include <requesters/discounts.hpp>
#include <requesters/utils.hpp>
#include <tests/utils.hpp>
#include <validators.hpp>

namespace eats_discounts_applicator::tests {

namespace {

struct TestParams {
  int64_t place_id;
  std::unordered_map<std::string, std::vector<PlaceDiscountMeta>> discounts;
  std::unordered_map<int64_t, std::vector<PlaceDiscount>> fetched_discounts;
  std::unordered_set<std::string> merge_promo_types;
  std::string test_name;
};

class TestMergeCartDiscounts : public testing::TestWithParam<TestParams> {};

std::string PrintToString(const TestParams& params) { return params.test_name; }

const std::vector<TableData> kTableMoneyData = {
    TableData{DiscountType::AbsoluteValue /*type*/, "500" /*from cost*/,
              "15" /*value*/},
    TableData{DiscountType::FractionWithMaximum /*type*/, "1000" /*from cost*/,
              "60" /*value*/},
};

const std::vector<TableData> kTableCombineData = {
    TableData{DiscountType::ProductValue /*type*/, "1000" /*from cost*/,
              "787" /*value*/},
    TableData{DiscountType::FractionWithMaximum /*type*/, "1000" /*from cost*/,
              "10" /*value*/},
};

const std::vector<TestParams> kBasicTestParams = {
    {1,  // place_id
     std::unordered_map<std::string, std::vector<PlaceDiscountMeta>>{
         {ToString(clients::eats_discounts::HierarchyName::kCartDiscounts),
          {{Money(100), Money(100), "discount", "", "",
            ToString(clients::eats_discounts::HierarchyName::kCartDiscounts),
            100, "super_discount", std::nullopt,
            DiscountTypeForThreshold::kDiscount}}},
         {ToString(
              clients::eats_discounts::HierarchyName::kRestaurantDiscounts),
          {{Money(100), Money(100), "discount", "", "",
            ToString(
                clients::eats_discounts::HierarchyName::kRestaurantDiscounts),
            100, "super_discount", std::nullopt,
            DiscountTypeForThreshold::kDiscount}}}},  // discounts
     std::unordered_map<int64_t, std::vector<PlaceDiscount>>{
         {1,
          {{"discount", "", "", Money(100), 100, "super_discount",
            std::nullopt}}}},  // fetched_discounts
     {"100"},                  // merge_promo_types
     "super_test_merge"},
    {1,  // place_id
     std::unordered_map<std::string, std::vector<PlaceDiscountMeta>>{
         {ToString(clients::eats_discounts::HierarchyName::kCartDiscounts),
          {{Money(100), Money(100), "discount1", "", "",
            ToString(clients::eats_discounts::HierarchyName::kCartDiscounts),
            100, "super_discount", std::nullopt,
            DiscountTypeForThreshold::kDiscount}}},
         {ToString(
              clients::eats_discounts::HierarchyName::kRestaurantDiscounts),
          {{Money(100), Money(100), "discount2", "", "",
            ToString(
                clients::eats_discounts::HierarchyName::kRestaurantDiscounts),
            101, "no_super_discount", std::nullopt,
            DiscountTypeForThreshold::kDiscount}}}},  // discounts
     std::unordered_map<int64_t, std::vector<PlaceDiscount>>{
         {1,
          {{"discount1", "", "", Money(100), 100, "super_discount",
            std::nullopt},
           {"discount2", "", "", Money(100), 101, "no_super_discount",
            std::nullopt}}}},  // fetched_discounts
     {"100"},                  // merge_promo_types
     "super_test_no_merge"}};

}  // namespace

TEST_P(TestMergeCartDiscounts, BasicTest) {
  const auto params = GetParam();
  std::unordered_map<int64_t, std::vector<PlaceDiscount>> result;
  requesters::MergeCartDiscounts(params.place_id, params.discounts, result,
                                 params.merge_promo_types);
  EXPECT_EQ(result.size(), params.fetched_discounts.size());
  EXPECT_EQ(result.at(1).size(), params.fetched_discounts.at(1).size());
}

INSTANTIATE_TEST_SUITE_P(/* no prefix */, TestMergeCartDiscounts,
                         testing::ValuesIn(kBasicTestParams),
                         testing::PrintToStringParamName());

}  // namespace eats_discounts_applicator::tests
