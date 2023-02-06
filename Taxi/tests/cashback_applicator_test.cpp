#include <gtest/gtest.h>

#include <applicators/menu.hpp>
#include <tests/utils.hpp>

namespace eats_discounts_applicator::tests {

namespace {

template <class Params>
void AssertResult(const AppliedCashbacks& menu_result, const Params& params) {
  EXPECT_EQ(menu_result.size(), params.exp_menu.size());
  for (const auto& [product_id, item] : menu_result) {
    const auto& it = params.exp_menu.find(product_id);
    EXPECT_NE(it, params.exp_menu.end());
    EXPECT_EQ(item.public_id, it->second.public_id);
    EXPECT_EQ(item.price, it->second.price);
    EXPECT_EQ(item.promo_price, it->second.promo_price);
    if (item.promo_price) {
      EXPECT_EQ(*item.promo_price, *it->second.promo_price);
    }
    EXPECT_EQ(item.promo_type.has_value(), it->second.promo_type.has_value());
    if (item.promo_type) {
      const auto& promo = item.promo_type.value();
      const auto& exp_promo = it->second.promo_type.value();
      EXPECT_EQ(promo.id, exp_promo.id);
      EXPECT_EQ(promo.name, exp_promo.name);
      EXPECT_EQ(promo.value, exp_promo.value);
    }
  }
}

}  // namespace

namespace cashback_category {

struct TestParams {
  std::vector<MenuItemForCashback> menu_items;
  FetchedCashbacks cashbacks;
  AppliedCashbacks exp_menu;
  std::string test_name;
};

class TestCashbackCategory : public testing::TestWithParam<TestParams> {};

std::string PrintToString(const TestParams& params) { return params.test_name; }

const std::vector<TestParams> kTestParams = {
    {
        {{"1", Money(100), std::nullopt}},
        {},
        {{"1", {"1", Money(100), std::nullopt, std::nullopt}}},
        "no_cashback",
    },
    {
        {{"1", Money(100), std::nullopt}},
        {MakeFetchedCashbacks(
            {{"2", CashbackType::AbsoluteValue, "10", std::nullopt}})},
        {{"1", {"1", Money(100), std::nullopt, std::nullopt}}},
        "no_cashback_for_requested",
    },
    {
        {{"1", Money(100), std::nullopt}},
        {MakeFetchedCashbacks(
            {{"1", CashbackType::AbsoluteValue, "10", std::nullopt}})},
        {{"1", {"1", Money(100), std::nullopt, {{111, "Cashback", 10}}}}},
        "absolute_cashback",
    },
    {
        {{"1", Money(100), Money(50)}},
        {MakeFetchedCashbacks(
            {{"1", CashbackType::AbsoluteValue, "10", std::nullopt}})},
        {{"1", {"1", Money(100), Money(50), {{111, "Cashback", 10}}}}},
        "absolute_cashback_with_promo",
    },
    {
        {{"1", Money(100), std::nullopt}},
        {MakeFetchedCashbacks(
            {{"1", CashbackType::FractionWithMaximum, "15", std::nullopt}})},
        {{"1", {"1", Money(100), std::nullopt, {{111, "Cashback", 15}}}}},
        "fraction_cashback",
    },
    {
        {{"1", Money(11), std::nullopt}},
        {MakeFetchedCashbacks(
            {{"1", CashbackType::FractionWithMaximum, "10", std::nullopt}})},
        {{"1", {"1", Money(11), std::nullopt, {{111, "Cashback", 1}}}}},
        "fraction_round_low_cashback",
    },
    {
        {{"1", Money(19), std::nullopt}},
        {MakeFetchedCashbacks(
            {{"1", CashbackType::FractionWithMaximum, "10", std::nullopt}})},
        {{"1", {"1", Money(19), std::nullopt, {{111, "Cashback", 1}}}}},
        "fraction_round_high_cashback",
    },
    {
        {{"1", Money(200), Money(100)}},
        {MakeFetchedCashbacks(
            {{"1", CashbackType::FractionWithMaximum, "15", std::nullopt}})},
        {{"1", {"1", Money(200), Money(100), {{111, "Cashback", 15}}}}},
        "fraction_cashback_with_promo",
    },
    {
        {{"1", Money(100), std::nullopt}},
        {MakeFetchedCashbacks(
            {{"1", CashbackType::FractionWithMaximum, "15", "10"}})},
        {{"1", {"1", Money(100), std::nullopt, {{111, "Cashback", 10}}}}},
        "fraction_with_max_cashback",
    },
    {
        {{"1", Money(100), std::nullopt}},
        {MakeFetchedCashbacks(
            {{"1", CashbackType::TableValue, "10", std::nullopt}})},
        {{"1", {"1", Money(100), std::nullopt, std::nullopt}}},
        "table_cashback",
    },
    {
        {{"1", Money(50), std::nullopt}},
        {MakeFetchedCashbacks(
            {{"1", CashbackType::TableValue, "10", std::nullopt}})},
        {{"1", {"1", Money(50), std::nullopt, std::nullopt}}},
        "no_table_cashback",
    },
    {
        {{"1", Money(100), std::nullopt}},
        {MakeFetchedCashbacks(
            {{"1", CashbackType::AbsoluteValue, "500", std::nullopt}})},
        {{"1", {"1", Money(100), std::nullopt, {{111, "Cashback", 100}}}}},
        "absolute_cashback_more_than_price",
    },
    {
        {{"1", Money(100), Money(40)}},
        {MakeFetchedCashbacks(
            {{"1", CashbackType::AbsoluteValue, "500", std::nullopt}})},
        {{"1", {"1", Money(100), Money(40), {{111, "Cashback", 40}}}}},
        "absolute_cashback_more_than_price_with_promo",
    },
    {
        {{"1", Money(100), std::nullopt}},
        {MakeFetchedCashbacks(
            {{"1", CashbackType::FractionWithMaximum, "100", std::nullopt}})},
        {{"1", {"1", Money(100), std::nullopt, {{111, "Cashback", 100}}}}},
        "fraction_cashback_100_percent",
    },
    {
        {{"1", Money(100), Money(50)}},
        {MakeFetchedCashbacks(
            {{"1", CashbackType::FractionWithMaximum, "100", std::nullopt}})},
        {{"1", {"1", Money(100), Money(50), {{111, "Cashback", 50}}}}},
        "fraction_cashback_100_percent_with_promo",
    },
    {
        {{"1", Money(100), std::nullopt}},
        {MakeFetchedCashbacks(
            {{"1", CashbackType::AbsoluteValue, "10", std::nullopt},
             {"1", CashbackType::AbsoluteValue, "20", std::nullopt}})},
        {{"1", {"1", Money(100), std::nullopt, {{111, "Cashback", 20}}}}},
        "chose_best_absolute_cashback",
    },
    {
        {{"1", Money(100), std::nullopt}},
        {MakeFetchedCashbacks(
            {{"1", CashbackType::AbsoluteValue, "20", std::nullopt},
             {"1", CashbackType::AbsoluteValue, "10", std::nullopt}})},
        {{"1", {"1", Money(100), std::nullopt, {{111, "Cashback", 20}}}}},
        "chose_best_absolute_cashback_reversed",
    },
    {
        {{"1", Money(100), std::nullopt}},
        {MakeFetchedCashbacks(
            {{"1", CashbackType::FractionWithMaximum, "10", std::nullopt},
             {"1", CashbackType::FractionWithMaximum, "20", std::nullopt}})},
        {{"1", {"1", Money(100), std::nullopt, {{111, "Cashback", 20}}}}},
        "chose_best_fractional_cashback",
    },
    {
        {{"1", Money(100), std::nullopt}},
        {MakeFetchedCashbacks(
            {{"1", CashbackType::AbsoluteValue, "21", std::nullopt},
             {"1", CashbackType::FractionWithMaximum, "20", std::nullopt}})},
        {{"1", {"1", Money(100), std::nullopt, {{111, "Cashback", 21}}}}},
        "chose_best_mixed_cashback",
    },
};

TEST_P(TestCashbackCategory, BasicTest) {
  const auto params = GetParam();
  auto menu_result = applicators::ApplyCashbackForCashbackCategory(
      params.menu_items, params.cashbacks);
  AssertResult(menu_result, params);
}

INSTANTIATE_TEST_SUITE_P(/* no prefix */, TestCashbackCategory,
                         testing::ValuesIn(kTestParams),
                         testing::PrintToStringParamName());

}  // namespace cashback_category

}  // namespace eats_discounts_applicator::tests
