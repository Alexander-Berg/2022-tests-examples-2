#include <gtest/gtest.h>

#include <optional>
#include <string>

#include <applicators/item_applier.hpp>
#include <applicators/menu.hpp>
#include <experiments3.hpp>
#include <tests/utils.hpp>

#include <clients/eats-discounts/definitions.hpp>

#include <eats-discounts-applicator/common.hpp>
#include <eats-discounts-applicator/models.hpp>

namespace eats_discounts_applicator::tests {

using DiscountApplier = eats_discounts_applicator::applicators::DiscountApplier;

namespace {

void AssertItem(const MenuItemWithDiscount& item,
                const MenuItemWithDiscount& expected_item) {
  EXPECT_EQ(item.public_id, expected_item.public_id);
  EXPECT_EQ(item.price, expected_item.price);
  EXPECT_EQ(item.promo_price, expected_item.promo_price);
  if (item.promo_price) {
    EXPECT_EQ(item.promo_price.value(), expected_item.promo_price.value());
  }
  EXPECT_EQ(item.promo_types.size(), expected_item.promo_types.size());
  for (size_t i = 0; i < item.promo_types.size(); ++i) {
    const auto& promo = item.promo_types[i];
    const auto& exp_promo = expected_item.promo_types[i];
    EXPECT_EQ(promo.id, exp_promo.id);
    EXPECT_EQ(promo.name, exp_promo.name);
    EXPECT_EQ(promo.picture_uri, exp_promo.picture_uri);
    EXPECT_EQ(promo.detailed_picture_url, exp_promo.detailed_picture_url);
  }
  EXPECT_EQ(item.options.size(), expected_item.options.size());
  for (size_t i = 0; i < item.options.size(); ++i) {
    const auto& option = item.options[i];
    const auto& exp_option = expected_item.options[i];
    EXPECT_EQ(option.id, exp_option.id);
    EXPECT_EQ(option.price, exp_option.price);
    EXPECT_EQ(option.promo_price, exp_option.promo_price);
  }
}

void AssertItem(const MenuItemWithDiscounts& item,
                const MenuItemWithDiscounts& expected_item) {
  EXPECT_EQ(item.public_id, expected_item.public_id);
  EXPECT_EQ(item.price, expected_item.price);
  EXPECT_EQ(item.promo_price, expected_item.promo_price);
  if (item.promo_price) {
    EXPECT_EQ(item.promo_price.value(), expected_item.promo_price.value());
  }
  EXPECT_EQ(item.discount_promos.size(), expected_item.discount_promos.size());
  for (size_t i = 0; i < item.discount_promos.size(); ++i) {
    const auto& promo = item.discount_promos[i];
    const auto& exp_promo = expected_item.discount_promos[i];
    EXPECT_EQ(promo.id, exp_promo.id);
    EXPECT_EQ(promo.name, exp_promo.name);
    EXPECT_EQ(promo.picture_uri, exp_promo.picture_uri);
    EXPECT_EQ(promo.detailed_picture_url, exp_promo.detailed_picture_url);
  }
  EXPECT_EQ(item.cashback_promo.has_value(),
            expected_item.cashback_promo.has_value());
  if (item.cashback_promo.has_value()) {
    EXPECT_EQ(item.cashback_promo.value().value,
              expected_item.cashback_promo.value().value);
    EXPECT_EQ(item.cashback_promo.value().id,
              expected_item.cashback_promo.value().id);
    EXPECT_EQ(item.cashback_promo.value().name,
              expected_item.cashback_promo.value().name);
  }
  EXPECT_EQ(item.options.size(), expected_item.options.size());
  for (size_t i = 0; i < item.options.size(); ++i) {
    const auto& option = item.options[i];
    const auto& exp_option = expected_item.options[i];
    EXPECT_EQ(option.id, exp_option.id);
    EXPECT_EQ(option.price, exp_option.price);
    EXPECT_EQ(option.promo_price, exp_option.promo_price);
  }
}

template <class Params, class MenuItem>
void AssertResult(const std::unordered_map<std::string, MenuItem>& menu_result,
                  const Params& params) {
  EXPECT_EQ(menu_result.size(), params.exp_menu.size());
  for (const auto& [id, item] : menu_result) {
    const auto& it = params.exp_menu.find(id);
    EXPECT_NE(it, params.exp_menu.end());
    AssertItem(item, it->second);
  }
}

}  // namespace

namespace menu_applicator {

struct TestParams {
  std::vector<MenuItemForDiscount> menu_items;
  requesters::MatchedDiscounts discounts_response;
  std::unordered_map<std::string, MenuItemWithDiscounts> exp_menu;
  std::string test_name;
};

class TestMenuApplicator : public testing::TestWithParam<TestParams> {};

std::string PrintToString(const TestParams& params) { return params.test_name; }

const std::vector<TestParams> kBasicTestParams = {
    {
        {{"1", Money(100), std::nullopt, {}}},
        MakeResponses(DiscountType::NoDiscount, kEmptyExcludedInformation,
                      kPromoTypesInfo),
        {{"1", {"1", Money(100), std::nullopt, {}, std::nullopt, {}}}},
        "no_discounts",
    },
    {
        {{"1", Money(100), Money(40), {}}},
        MakeResponses(DiscountType::NoDiscount, kEmptyExcludedInformation,
                      kPromoTypesInfo),
        {{"1", {"1", Money(100), Money(40), {}, std::nullopt, {}}}},
        "no_discounts_with_promo",
    },
    {
        {{"1", Money(100), std::nullopt, {}}},
        MakeResponses(DiscountType::AbsoluteValue, kEmptyExcludedInformation,
                      kPromoTypesInfo, "10"),
        {{"1",
          {"1",
           Money(100),
           Money(90),
           {{impl::kMoneyTypeId, impl::kMoneyTypeName, "picture_uri",
             std::nullopt}},
           std::nullopt,
           {}}}},
        "absolute_discounts",
    },
    {
        {{"1", Money(1000), std::nullopt, {}}},
        MakeResponses(DiscountType::FractionWithMaximum,
                      kEmptyExcludedInformation, kPromoTypesInfo, "10"),
        {{"1",
          {"1",
           Money(1000),
           Money(900),
           {{impl::kMoneyTypeId, impl::kMoneyTypeName, "picture_uri",
             std::nullopt}},
           std::nullopt,
           {}}}},
        "fraction_with_max_discounts_no_max",
    },
    {
        {{"1", Money(1000), std::nullopt, {}}},
        MakeResponses(DiscountType::FractionWithMaximum,
                      kEmptyExcludedInformation, kPromoTypesInfo, "20", "150"),
        {{"1",
          {"1",
           Money(1000),
           Money(850),
           {{impl::kMoneyTypeId, impl::kMoneyTypeName, "picture_uri",
             std::nullopt}},
           std::nullopt,
           {}}}},
        "fraction_with_max_discounts",
    },
    {
        {{"1", Money(150), std::nullopt, {}}},
        MakeResponses(DiscountType::TableValue, kEmptyExcludedInformation,
                      kPromoTypesInfo),
        {{"1", {"1", Money(150), std::nullopt, {}, std::nullopt, {}}}},
        "table_discount",
    },
    {
        {{"1",
          Money(1000),
          Money(500),
          {{25, "retail_name", "retail_uri", std::nullopt}}}},
        MakeResponses(DiscountType::FractionWithMaximum,
                      kEmptyExcludedInformation, kPromoTypesInfo, "10"),
        {{"1",
          {"1",
           Money(1000),
           Money(450),
           {{impl::kMoneyTypeId, impl::kMoneyTypeName, "picture_uri",
             std::nullopt}},
           std::nullopt,
           {}}}},
        "disc_from_retail_bigger_both_applied",
    },
    {
        {{"1",
          Money(1000),
          Money(999),
          {{25, "retail_name", "retail_uri", std::nullopt}}}},
        MakeResponses(DiscountType::FractionWithMaximum,
                      kEmptyExcludedInformation, kPromoTypesInfo, "10"),
        {{"1",
          {"1",
           Money(1000),
           Money("899.1"),
           {{impl::kMoneyTypeId, impl::kMoneyTypeName, "picture_uri",
             std::nullopt}},
           std::nullopt,
           {}}}},
        "disc_from_us_bigger_both_applied",
    },
    {
        {{"1", Money(100), std::nullopt, {}}},
        MakeResponses(DiscountType::ProductValue, kEmptyExcludedInformation,
                      kPromoTypesInfo),
        {{"1",
          {"1",
           Money(100),
           std::nullopt,
           {{impl::kProductTypeId, impl::kProductTypeName, "picture_uri",
             std::nullopt}},
           std::nullopt,
           {}}}},
        "product_discount",
    },
    {
        {{"1",
          Money(100),
          Money(90),
          {{1, "name", "picture_uri", std::nullopt}}}},
        MakeResponses(DiscountType::ProductValue, kEmptyExcludedInformation,
                      kPromoTypesInfo),
        {{"1",
          {"1",
           Money(100),
           Money(90),
           {{1, "name", "picture_uri", std::nullopt}},
           std::nullopt,
           {}}}},
        "product_discount_already_has_discount",
    },
    {
        {{"1", Money(100), std::nullopt, {}}},
        MakeResponses(DiscountType::ProductWithAbsoluteValue,
                      kEmptyExcludedInformation, kPromoTypesInfo, "50"),
        {{"1",
          {"1",
           Money(100),
           Money(50),
           {{impl::kMoneyTypeId, impl::kMoneyTypeName, "picture_uri",
             std::nullopt}},
           std::nullopt,
           {}}}},
        "product_with_money_discount",
    },
    {
        {{{"1", Money(100), std::nullopt, {}}}},
        requesters::ParseMatchResponse(
            {MakePlaceCashbackResponse(CashbackType::AbsoluteValue, "10",
                                       std::nullopt, "2")},
            kEmptyExcludedInformation, kPromoTypesInfo),
        {{"1", {"1", Money(100), std::nullopt, {}, std::nullopt, {}}}},
        "no_cashback_for_item",
    },
    {
        {{{"1", Money(100), std::nullopt, {}}}},
        requesters::ParseMatchResponse(
            {MakePlaceCashbackResponse(CashbackType::AbsoluteValue)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        {{"1",
          {"1", Money(100), std::nullopt, {}, {{111, "Cashback", 10}}, {}}}},
        "absolute_cashback",
    },
    {
        {{{"1", Money(100), std::nullopt, {}}}},
        requesters::ParseMatchResponse(
            {MakePlaceCashbackResponse(CashbackType::FractionWithMaximum,
                                       "15")},
            kEmptyExcludedInformation, kPromoTypesInfo),
        {{"1",
          {"1", Money(100), std::nullopt, {}, {{111, "Cashback", 15}}, {}}}},
        "fraction_cashback",
    },
    {
        {{{"1", Money(200), Money(100), {}}}},
        requesters::ParseMatchResponse(
            {MakePlaceCashbackResponse(CashbackType::FractionWithMaximum,
                                       "15")},
            kEmptyExcludedInformation, kPromoTypesInfo),
        {{"1", {"1", Money(200), Money(100), {}, {{111, "Cashback", 15}}, {}}}},
        "fraction_cashback_with_promo",
    },
    {
        {{{"1", Money(100), std::nullopt, {}}}},
        requesters::ParseMatchResponse(
            {MakePlaceCashbackResponse(CashbackType::FractionWithMaximum, "15",
                                       "10")},
            kEmptyExcludedInformation, kPromoTypesInfo),
        {{"1",
          {"1", Money(100), std::nullopt, {}, {{111, "Cashback", 10}}, {}}}},
        "fraction_with_max_cashback",
    },
    {
        {{{"1", Money(11), std::nullopt, {}}}},
        requesters::ParseMatchResponse(
            {MakePlaceCashbackResponse(CashbackType::FractionWithMaximum,
                                       "10")},
            kEmptyExcludedInformation, kPromoTypesInfo),
        {{"1", {"1", Money(11), std::nullopt, {}, {{111, "Cashback", 1}}, {}}}},
        "fraction_round_low_cashback",
    },
    {
        {{{"1", Money(19), std::nullopt, {}}}},
        requesters::ParseMatchResponse(
            {MakePlaceCashbackResponse(CashbackType::FractionWithMaximum,
                                       "10")},
            kEmptyExcludedInformation, kPromoTypesInfo),
        {{"1", {"1", Money(19), std::nullopt, {}, {{111, "Cashback", 1}}, {}}}},
        "fraction_round_high_cashback",
    },
    {
        {{{"1", Money(100), std::nullopt, {}}}},
        requesters::ParseMatchResponse(
            {MakePlaceCashbackResponse(CashbackType::TableValue)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        {{"1", {"1", Money(100), std::nullopt, {}, std::nullopt, {}}}},
        "table_cashback",
    },
    {
        {{{"1", Money(100), std::nullopt, {}}}},
        requesters::ParseMatchResponse(
            {MakePlaceCashbackResponse(CashbackType::AbsoluteValue, "500")},
            kEmptyExcludedInformation, kPromoTypesInfo),
        {{"1",
          {"1", Money(100), std::nullopt, {}, {{111, "Cashback", 100}}, {}}}},
        "absolute_cashback_more_than_price",
    },
    {
        {{{"1", Money(100), Money(50), {}}}},
        requesters::ParseMatchResponse(
            {MakePlaceCashbackResponse(CashbackType::AbsoluteValue, "500")},
            kEmptyExcludedInformation, kPromoTypesInfo),
        {{"1", {"1", Money(100), Money(50), {}, {{111, "Cashback", 50}}, {}}}},
        "absolute_cashback_more_than_promo_price",
    },
    {
        {{{"1", Money(100), std::nullopt, {}}}},
        requesters::ParseMatchResponse(
            {MakePlaceCashbackResponse(CashbackType::FractionWithMaximum,
                                       "100")},
            kEmptyExcludedInformation, kPromoTypesInfo),
        {{"1",
          {"1", Money(100), std::nullopt, {}, {{111, "Cashback", 100}}, {}}}},
        "fraction_cashback_100_percent",
    },
    {
        {{{"1", Money(100), Money(50), {}}}},
        requesters::ParseMatchResponse(
            {MakePlaceCashbackResponse(CashbackType::FractionWithMaximum,
                                       "100")},
            kEmptyExcludedInformation, kPromoTypesInfo),
        {{"1", {"1", Money(100), Money(50), {}, {{111, "Cashback", 50}}, {}}}},
        "fraction_cashback_100_percent_with_promo",
    },
    {
        {{{"1", Money(100), std::nullopt, {}}}},
        requesters::ParseMatchResponse(
            {MakePlaceCashbackResponse(CashbackType::AbsoluteValue),
             MakeYandexCashbackResponse(CashbackType::AbsoluteValue, "15")},
            kEmptyExcludedInformation, kPromoTypesInfo),
        {{"1",
          {"1", Money(100), std::nullopt, {}, {{111, "Cashback", 15}}, {}}}},
        "absolute_cashbacks_yandex_better",
    },
    {
        {{{"1", Money(100), std::nullopt, {}}}},
        requesters::ParseMatchResponse(
            {MakePlaceCashbackResponse(CashbackType::AbsoluteValue, "15"),
             MakeYandexCashbackResponse(CashbackType::AbsoluteValue)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        {{"1",
          {"1", Money(100), std::nullopt, {}, {{111, "Cashback", 15}}, {}}}},
        "absolute_cashbacks_place_better",
    },
    {
        {{{"1", Money(100), std::nullopt, {}}}},
        requesters::ParseMatchResponse(
            {MakePlaceCashbackResponse(CashbackType::FractionWithMaximum, "15"),
             MakeYandexCashbackResponse(CashbackType::AbsoluteValue)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        {{"1",
          {"1", Money(100), std::nullopt, {}, {{111, "Cashback", 15}}, {}}}},
        "fraction_cashbacks_place_better",
    },
    {
        {{{"1", Money(100), std::nullopt, {}}}},
        requesters::ParseMatchResponse(
            {MakePlaceCashbackResponse(CashbackType::FractionWithMaximum),
             MakeYandexCashbackResponse(CashbackType::AbsoluteValue, "15")},
            kEmptyExcludedInformation, kPromoTypesInfo),
        {{"1",
          {"1", Money(100), std::nullopt, {}, {{111, "Cashback", 15}}, {}}}},
        "fraction_cashbacks_yandex_better",
    },
    {
        {{{"1", Money(100), std::nullopt, {}}}},
        requesters::ParseMatchResponse(
            {MakePlaceCashbackResponse(CashbackType::FractionWithMaximum),
             MakeYandexCashbackResponse(CashbackType::AbsoluteValue, "15")},
            kEmptyExcludedInformation, kPromoTypesInfo),
        {{"1",
          {"1", Money(100), std::nullopt, {}, {{111, "Cashback", 15}}, {}}}},
        "mixed_cashbacks_absolute_better",
    },
    {
        {{{"1", Money(100), std::nullopt, {}}}},
        requesters::ParseMatchResponse(
            {MakePlaceCashbackResponse(CashbackType::FractionWithMaximum, "15"),
             MakeYandexCashbackResponse(CashbackType::AbsoluteValue)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        {{"1",
          {"1", Money(100), std::nullopt, {}, {{111, "Cashback", 15}}, {}}}},
        "mixed_cashbacks_fraction_better",
    },
    {
        {{{"1", Money(100), std::nullopt, {}}}},
        requesters::ParseMatchResponse(
            {MakePlaceCashbackResponse(CashbackType::AbsoluteValue),
             MakeMenuDiscountResponse(DiscountType::AbsoluteValue)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        {{"1",
          {"1",
           Money(100),
           Money(90),
           {{impl::kMoneyTypeId, impl::kMoneyTypeName, "picture_uri",
             std::nullopt}},
           {{111, "Cashback", 10}},
           {}}}},
        "absolute_discount_and_cashback",
    },
    {
        {{{"1", Money(100), std::nullopt, {}}}},
        requesters::ParseMatchResponse(
            {MakePlaceCashbackResponse(CashbackType::FractionWithMaximum),
             MakeMenuDiscountResponse(DiscountType::FractionWithMaximum)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        {{"1",
          {"1",
           Money(100),
           Money(90),
           {{impl::kMoneyTypeId, impl::kMoneyTypeName, "picture_uri",
             std::nullopt}},
           {{111, "Cashback", 9}},
           {}}}},
        "fractional_discount_and_cashback",
    },
    {
        {{{"1", Money(150), Money(100), {}}}},
        requesters::ParseMatchResponse(
            {MakePlaceCashbackResponse(CashbackType::FractionWithMaximum),
             MakeMenuDiscountResponse(DiscountType::FractionWithMaximum)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        {{"1",
          {"1",
           Money(150),
           Money(90),
           {{impl::kMoneyTypeId, impl::kMoneyTypeName, "picture_uri",
             std::nullopt}},
           {{111, "Cashback", 9}},
           {}}}},
        "fractional_discount_and_cashback_with_promo",
    },
    {
        {{"1", Money(100), std::nullopt, {}}},
        MakeResponses(DiscountType::AbsoluteValue,
                      experiments::ExcludedInformation{
                          {}, {ExpDiscountType::kYandexMenuMoneyDiscount}},
                      kPromoTypesInfo, "10"),
        {{"1", {"1", Money(100), std::nullopt, {}, std::nullopt, {}}}},
        "absolute_discount_disable_by_exp",
    },
    {
        {{"1", Money(100), std::nullopt, {}}},
        MakeResponses(DiscountType::ProductValue,
                      experiments::ExcludedInformation{
                          {}, {ExpDiscountType::kYandexMenuProductDiscount}},
                      kPromoTypesInfo),
        {{"1", {"1", Money(100), std::nullopt, {}, std::nullopt, {}}}},
        "product_discount_disable_by_exp",
    },
    {
        {MenuItemForDiscount{
            "1",
            Money(100),
            std::nullopt,
            {},
            {{5, Money(10)}, {2, Money(15)}}}},
        MakeResponses(DiscountType::NoDiscount, kEmptyExcludedInformation,
                      kPromoTypesInfo),
        {
            {"1",
             {
                 "1",
                 Money(100),
                 std::nullopt,
                 {},
                 std::nullopt,
                 {{5, Money(10), std::nullopt},
                  {2, Money(15), std::nullopt}},  // options
             }},
        },
        "no_discounts_options",
    },
    {
        {MenuItemForDiscount{
            "1",
            Money(100),
            std::nullopt,
            {},
            {{5, Money(10)}, {2, Money(15)}}}},
        MakeResponses(DiscountType::AbsoluteValue, kEmptyExcludedInformation,
                      kPromoTypesInfo, "10"),
        {
            {"1",
             {
                 "1",
                 Money(100),
                 Money(90),
                 {{impl::kMoneyTypeId, impl::kMoneyTypeName, "picture_uri",
                   std::nullopt}},
                 std::nullopt,
                 {{5, Money(10), std::nullopt},
                  {2, Money(15), std::nullopt}},  // options
             }},
        },
        "absolute_discounts_options",
    },
    {
        {{"1",
          Money(1000),
          std::nullopt,
          {},
          {{5, Money(10)}, {2, Money(15)}}}},
        MakeResponses(DiscountType::FractionWithMaximum,
                      kEmptyExcludedInformation, kPromoTypesInfo, "20", "150"),
        {{"1",
          {"1",
           Money(1000),
           Money(850),
           {{impl::kMoneyTypeId, impl::kMoneyTypeName, "picture_uri",
             std::nullopt}},
           std::nullopt,
           {{5, Money(10), Money(8)}, {2, Money(15), Money(12)}}}}},
        "fraction_with_max_discounts_options",
    },
    {
        {{"1", Money(150), std::nullopt, {}, {{5, Money(10)}, {2, Money(15)}}}},
        MakeResponses(DiscountType::TableValue, kEmptyExcludedInformation,
                      kPromoTypesInfo),
        {{"1",
          {"1",
           Money(150),
           std::nullopt,
           {},
           std::nullopt,
           {{5, Money(10), std::nullopt}, {2, Money(15), std::nullopt}}}}},
        "table_discount_options",
    },
};

TEST_P(TestMenuApplicator, BasicTest) {
  const auto params = GetParam();
  auto menu_result = applicators::ApplyDiscountsAndCashbackForMenu(
      params.menu_items, params.discounts_response);
  AssertResult(menu_result, params);
}

INSTANTIATE_TEST_SUITE_P(/* no prefix */, TestMenuApplicator,
                         testing::ValuesIn(kBasicTestParams),
                         testing::PrintToStringParamName());

}  // namespace menu_applicator

impl::DiscountWithMeta<clients::eats_discounts::V2MatchedMoneyProductDiscount>
MakeDiscount(
    const clients::eats_discounts::V2MatchedMoneyProductDiscount& discount) {
  return impl::DiscountWithMeta(discount, kPromoTypesInfo, "menu_discounts");
}

namespace discount_category {

struct DiscountCategoryTestParams {
  std::vector<MenuItemForDiscount> menu_items;
  FetchedDiscounts discounts;
  std::unordered_map<std::string, MenuItemWithDiscount> exp_menu;
  std::string test_name;
};

class TestDiscountCategory
    : public testing::TestWithParam<DiscountCategoryTestParams> {};

std::string PrintToString(const DiscountCategoryTestParams& params) {
  return params.test_name;
}

const std::vector<DiscountCategoryTestParams> kDiscountCategoryTestParams = {
    {
        {{"1", Money(100), std::nullopt, {}}},
        {},
        {{"1", {"1", Money(100), std::nullopt, {}, {}}}},
        "no_discounts",
    },
    {
        {{"1", Money(100), Money(40), {}}},
        {},
        {{"1", {"1", Money(100), Money(40), {}, {}}}},
        "no_discounts_with_promo",
    },
    {
        {{"1", Money(100), std::nullopt, {}}},
        {{"2",
          {MakeDiscount(
              MakeV2MenuDiscount(DiscountType::AbsoluteValue, "100"))}}},
        {{"1", {"1", Money(100), std::nullopt, {}, {}}}},
        "no_discounts_for_requested",
    },
    {
        {{"1", Money(100), std::nullopt, {}}},
        {{"1",
          {MakeDiscount(
              MakeV2MenuDiscount(DiscountType::AbsoluteValue, "50"))}}},
        {{"1",
          {"1",
           Money(100),
           Money(50),
           {{impl::kMoneyTypeId, impl::kMoneyTypeName, "picture_uri",
             std::nullopt}},
           {}}}},
        "absolute_discount",
    },
    {
        {{"1", Money(100), Money(50), {}}},
        {{"1",
          {MakeDiscount(
              MakeV2MenuDiscount(DiscountType::AbsoluteValue, "20"))}}},
        {{"1",
          {"1",
           Money(100),
           Money(30),
           {{impl::kMoneyTypeId, impl::kMoneyTypeName, "picture_uri",
             std::nullopt}},
           {}}}},
        "absolute_discount_smaller",
    },
    {
        {{"1", Money(1000), std::nullopt, {}}},
        {{"1",
          {MakeDiscount(
              MakeV2MenuDiscount(DiscountType::FractionWithMaximum, "10"))}}},
        {{"1",
          {"1",
           Money(1000),
           Money(900),
           {{impl::kMoneyTypeId, impl::kMoneyTypeName, "picture_uri",
             std::nullopt}},
           {}}}},
        "fraction_with_max_discounts_no_max",
    },
    {
        {{"1", Money(1000), std::nullopt, {}}},
        {{"1",
          {MakeDiscount(MakeV2MenuDiscount(DiscountType::FractionWithMaximum,
                                           "20", "150"))}}},
        {{"1",
          {"1",
           Money(1000),
           Money(850),
           {{impl::kMoneyTypeId, impl::kMoneyTypeName, "picture_uri",
             std::nullopt}},
           {}}}},
        "fraction_with_max_discounts",
    },
    {
        {{"1", Money(150), std::nullopt, {}}},
        {{"1", {MakeDiscount(MakeV2MenuDiscount(DiscountType::TableValue))}}},
        {{"1", {"1", Money(150), std::nullopt, {}, {}}}},
        "table_discount",
    },
    {
        {{"1", Money(500), std::nullopt, {}}},
        {{"1", {MakeDiscount(MakeV2MenuDiscount(DiscountType::ProductValue))}}},
        {{"1",
          {"1",
           Money(500),
           std::nullopt,
           {{impl::kProductTypeId, impl::kProductTypeName, "picture_uri",
             std::nullopt}},
           {}}}},
        "product_discount",
    },
    {
        {{"1", Money(500), Money(450), {}}},
        {{"1", {MakeDiscount(MakeV2MenuDiscount(DiscountType::ProductValue))}}},
        {{"1", {"1", Money(500), Money(450), {}, {}}}},
        "product_discount_already_has_discount",
    },
    {
        {{"1", Money(500), std::nullopt, {}}},
        {{"1",
          {MakeDiscount(MakeV2MenuDiscount(
              DiscountType::ProductWithAbsoluteValue, "50"))}}},
        {{"1",
          {"1",
           Money(500),
           Money(450),
           {{impl::kMoneyTypeId, impl::kMoneyTypeName, "picture_uri",
             std::nullopt}},
           {}}}},
        "product_with_absolute_discount",
    },
    {
        {{"1", Money(100), std::nullopt, {}},
         {"2", Money(200), Money(190), {}}},
        {{"1",
          {MakeDiscount(
              MakeV2MenuDiscount(DiscountType::AbsoluteValue, "50"))}},
         {"2",
          {MakeDiscount(
              MakeV2MenuDiscount(DiscountType::AbsoluteValue, "100"))}}},
        {{"1",
          {"1",
           Money(100),
           Money(50),
           {{impl::kMoneyTypeId, impl::kMoneyTypeName, "picture_uri",
             std::nullopt}},
           {}}},
         {"2",
          {"2",
           Money(200),
           Money(90),
           {{impl::kMoneyTypeId, impl::kMoneyTypeName, "picture_uri",
             std::nullopt}},
           {}}}},
        "absolute_discount_multiple_items",
    },
};

TEST_P(TestDiscountCategory, BasicTest) {
  const auto params = GetParam();
  auto menu_result = applicators::ApplyDiscountsForDiscountCategory(
      params.menu_items, params.discounts);
  AssertResult(menu_result, params);
}

INSTANTIATE_TEST_SUITE_P(/* no prefix */, TestDiscountCategory,
                         testing::ValuesIn(kDiscountCategoryTestParams),
                         testing::PrintToStringParamName());

}  // namespace discount_category

namespace agregate_discounts {

struct AgregateDiscountsTestParams {
  MenuItemForDiscount item;
  std::vector<DiscountApplier::Discount> matched_discounts;
  std::vector<DiscountInfo> discount_info;
  std::string test_name;
};

class TestAgregateMenuDiscounts
    : public testing::TestWithParam<AgregateDiscountsTestParams> {};

std::string PrintToString(const AgregateDiscountsTestParams& params) {
  return params.test_name;
}

const std::vector<AgregateDiscountsTestParams> kBasicTestParams = {
    {
        {"2", Money(200), Money(150), {}},  // item
        {DiscountApplier::Discount{
             MakeDiscount(MakeV2MenuDiscount(
                 DiscountType::AbsoluteValue, "15", std::nullopt, std::nullopt,
                 CustomPromoInfo{"test_discount", "discount for test",
                                 "http://test_promo.jpeg"},
                 "124")),
             impl::kPlace},
         DiscountApplier::Discount{
             MakeDiscount(MakeV2MenuDiscount(
                 DiscountType::AbsoluteValue, "120", std::nullopt, std::nullopt,
                 CustomPromoInfo{"test_discount2", "discount2 for test",
                                 "http://test_promo2.jpeg"},
                 "1001")),
             impl::kOwn}},  // matched_discounts
        CreateDiscountsInfo(
            {"124", "1001"},                              // discount_ids
            {"test_discount", "test_discount2"},          // names
            {"discount for test", "discount2 for test"},  // descriptions
            {"http://test_promo.jpeg",
             "http://test_promo2.jpeg"},  // picture_uris
            {Money(15), Money(120)},      // amounts
            {DiscountType::AbsoluteValue,
             DiscountType::AbsoluteValue},  // discount_types
            {"15", "120"},                  // discount_values
            {impl::kPlace, impl::kOwn},     // providers
            {std::nullopt, std::nullopt}    // additional_item_quantity
            ),                              // discounts_info
        "agregate_money_discounts"          // test_name
    },
    {
        {"2", Money(200), std::nullopt, {}},  // item
        {DiscountApplier::Discount{
             MakeDiscount(MakeV2MenuDiscount(
                 DiscountType::AbsoluteValue, "15", std::nullopt, std::nullopt,
                 CustomPromoInfo{"test_discount", "discount for test",
                                 "http://test_promo.jpeg"},
                 "124")),
             impl::kPlace},
         DiscountApplier::Discount{
             MakeDiscount(MakeV2MenuDiscount(DiscountType::ProductValue)),
             impl::kOwn}},                                  // matched_discounts
        CreateDiscountsInfo({"124"},                        // discount_ids
                            {"test_discount"},              // names
                            {"discount for test"},          // descriptions
                            {"http://test_promo.jpeg"},     // picture_uris
                            {Money(15)},                    // amounts
                            {DiscountType::AbsoluteValue},  // discount_types
                            {"15"},                         // discount_values
                            {impl::kPlace},                 // providers
                            {std::nullopt}      // additional_item_quantity
                            ),                  // discounts_info
        "agregate_money_and_product_discounts"  // test_name
    },
    {
        {"2", Money(200), std::nullopt, {}},  // item
        {DiscountApplier::Discount{
             MakeDiscount(MakeV2MenuDiscount(DiscountType::ProductValue)),
             impl::kPlace},
         DiscountApplier::Discount{
             MakeDiscount(MakeV2MenuDiscount(
                 DiscountType::AbsoluteValue, "15", std::nullopt, std::nullopt,
                 CustomPromoInfo{"test_discount", "discount for test",
                                 "http://test_promo.jpeg"},
                 "124")),
             impl::kOwn}},                                 // matched_discounts
        CreateDiscountsInfo({"21"},                        // discount_ids
                            {"name"},                      // names
                            {"descr"},                     // descriptions
                            {"picture_uri"},               // picture_uris
                            {Money(200)},                  // amounts
                            {DiscountType::ProductValue},  // discount_types
                            {"15"},                        // discount_values
                            {impl::kPlace},                // providers
                            {1}                 // additional_item_quantity
                            ),                  // discounts_info
        "agregate_product_and_money_discounts"  // test_name
    }};

TEST_P(TestAgregateMenuDiscounts, BasicTest) {
  const auto params = GetParam();
  DiscountApplier discount_applier{params.matched_discounts};
  auto result = discount_applier.AgregateDiscounts(params.item);
  for (size_t i = 0; i < result.size(); i++) {
    const auto& expected = params.discount_info[i];
    ASSERT_EQ(result[i].meta.id, expected.meta.id);
    ASSERT_EQ(result[i].meta.description, expected.meta.description);
    ASSERT_EQ(result[i].meta.picture_uri, expected.meta.picture_uri);
    ASSERT_EQ(result[i].meta.name, expected.meta.name);
    ASSERT_EQ(result[i].meta.type_id, expected.meta.type_id);
    ASSERT_EQ(result[i].meta.provider, expected.meta.provider);
    ASSERT_EQ(result[i].meta.amount, expected.meta.amount);

    ASSERT_EQ(result[i].payed_item_quantity, expected.payed_item_quantity);
    ASSERT_EQ(result[i].additional_item_quantity,
              expected.additional_item_quantity);
    ASSERT_EQ(result[i].money_value, expected.money_value);
  }
}

INSTANTIATE_TEST_SUITE_P(/* no prefix */, TestAgregateMenuDiscounts,
                         testing::ValuesIn(kBasicTestParams),
                         testing::PrintToStringParamName());

}  // namespace agregate_discounts

namespace apply_menu_discounts {

struct ApplyDiscountsTestParams {
  MenuItemForDiscount item;
  std::vector<DiscountApplier::Discount> matched_discounts;
  MenuItemWithDiscounts item_with_discount;
  std::string test_name;
};

class TestApplyMenuDiscounts
    : public testing::TestWithParam<ApplyDiscountsTestParams> {};

std::string PrintToString(const ApplyDiscountsTestParams& params) {
  return params.test_name;
}

const std::vector<ApplyDiscountsTestParams> kBasicTestParams = {
    // тест на суммирование абсолютных скидок
    {
        {
            "2",         // public_id
            Money(200),  // price
            Money(150),  // promo_price
            {},          // promo_types_in
            {}           // options
        },               // item
        {DiscountApplier::Discount{
             MakeDiscount(MakeV2MenuDiscount(
                 DiscountType::AbsoluteValue, "15", std::nullopt, std::nullopt,
                 CustomPromoInfo{"test_discount", "discount for test",
                                 "http://test_promo.jpeg"},
                 "1001")),
             impl::kPlace},
         DiscountApplier::Discount{
             MakeDiscount(MakeV2MenuDiscount(
                 DiscountType::AbsoluteValue, "120", std::nullopt, std::nullopt,
                 CustomPromoInfo{"test_discount2", "discount2 for test",
                                 "http://test_promo2.jpeg"},
                 "124")),
             impl::kOwn}},  // matched_discounts
        {
            "2",         // public_id
            Money(200),  // price
            Money(15),   // promo_price
            {{impl::kMoneyTypeId, impl::kMoneyTypeName,
              "http://test_promo.jpeg", std::nullopt},
             {impl::kMoneyTypeId, impl::kMoneyTypeName,
              "http://test_promo2.jpeg", std::nullopt}},  // discount_promos
            std::nullopt,                                 // cashback_promo
            {}                                            // options
        },                                                // item_with_discount
        "absolute_discounts",                             // test_name
    },
    // тест на суммирование абсолютных скидок, превышающих стоимость айтема
    {
        {
            "2",         // public_id
            Money(200),  // price
            Money(150),  // promo_price
            {},          // promo_types_in
            {}           // options
        },               // item
        {DiscountApplier::Discount{
             MakeDiscount(MakeV2MenuDiscount(
                 DiscountType::AbsoluteValue, "70", std::nullopt, std::nullopt,
                 CustomPromoInfo{"test_discount", "discount for test",
                                 "http://test_promo.jpeg"},
                 "1001")),
             impl::kPlace},
         DiscountApplier::Discount{
             MakeDiscount(MakeV2MenuDiscount(
                 DiscountType::AbsoluteValue, "90", std::nullopt, std::nullopt,
                 CustomPromoInfo{"test_discount2", "discount2 for test",
                                 "http://test_promo2.jpeg"},
                 "124")),
             impl::kOwn}},  // matched_discounts
        {
            "2",         // public_id
            Money(200),  // price
            Money(0),    // promo_price
            {{impl::kMoneyTypeId, impl::kMoneyTypeName,
              "http://test_promo.jpeg", std::nullopt},
             {impl::kMoneyTypeId, impl::kMoneyTypeName,
              "http://test_promo2.jpeg", std::nullopt}},  // discount_promos
            std::nullopt,                                 // cashback_promo
            {}                                            // options
        },                                                // item_with_discount
        "absolute_discounts_more_than_item_price",
    },
    // тест на суммирование процентных скидок
    {
        {
            "2",         // public_id
            Money(200),  // price
            Money(150),  // promo_price
            {},          // promo_types_in
            {}           // options
        },               // item
        {DiscountApplier::Discount{
             MakeDiscount(MakeV2MenuDiscount(
                 DiscountType::FractionWithMaximum, "20", std::nullopt,
                 std::nullopt,
                 CustomPromoInfo{"test_discount", "discount for test",
                                 "http://test_promo.jpeg"},
                 "1001")),
             impl::kPlace},
         DiscountApplier::Discount{
             MakeDiscount(MakeV2MenuDiscount(
                 DiscountType::FractionWithMaximum, "10", std::nullopt,
                 std::nullopt,
                 CustomPromoInfo{"test_discount2", "discount2 for test",
                                 "http://test_promo2.jpeg"},
                 "124")),
             impl::kOwn}},  // matched_discounts
        {
            "2",         // public_id
            Money(200),  // price
            Money(105),  // promo_price
            {{impl::kMoneyTypeId, impl::kMoneyTypeName,
              "http://test_promo.jpeg", std::nullopt},
             {impl::kMoneyTypeId, impl::kMoneyTypeName,
              "http://test_promo2.jpeg", std::nullopt}},  // discount_promos
            std::nullopt,                                 // cashback_promo
            {}                                            // options
        },                                                // item_with_discount
        "fraction_discounts",
    },
    // тест на суммирование процентных скидок превышающих 100%
    {
        {
            "2",         // public_id
            Money(200),  // price
            Money(150),  // promo_price
            {},          // promo_types_in
            {}           // options
        },               // item
        {DiscountApplier::Discount{
             MakeDiscount(MakeV2MenuDiscount(
                 DiscountType::FractionWithMaximum, "60", std::nullopt,
                 std::nullopt,
                 CustomPromoInfo{"test_discount", "discount for test",
                                 "http://test_promo.jpeg"},
                 "1001")),
             impl::kPlace},
         DiscountApplier::Discount{
             MakeDiscount(MakeV2MenuDiscount(
                 DiscountType::FractionWithMaximum, "50", std::nullopt,
                 std::nullopt,
                 CustomPromoInfo{"test_discount2", "discount2 for test",
                                 "http://test_promo2.jpeg"},
                 "124")),
             impl::kOwn}},  // matched_discounts
        {
            "2",         // public_id
            Money(200),  // price
            Money(0),    // promo_price
            {{impl::kMoneyTypeId, impl::kMoneyTypeName,
              "http://test_promo.jpeg", std::nullopt},
             {impl::kMoneyTypeId, impl::kMoneyTypeName,
              "http://test_promo2.jpeg", std::nullopt}},  // discount_promos
            std::nullopt,                                 // cashback_promo
            {}                                            // options
        },                                                // item_with_discount
        "fraction_discounts_more_than_100_percents",
    },
    // тест на абсолютную и процентную скидку
    {
        {
            "2",         // public_id
            Money(200),  // price
            Money(150),  // promo_price
            {},          // promo_types_in
            {}           // options
        },               // item
        {DiscountApplier::Discount{
             MakeDiscount(MakeV2MenuDiscount(
                 DiscountType::AbsoluteValue, "50", std::nullopt, std::nullopt,
                 CustomPromoInfo{"test_discount", "discount for test",
                                 "http://test_promo.jpeg"},
                 "1001")),
             impl::kPlace},
         DiscountApplier::Discount{
             MakeDiscount(MakeV2MenuDiscount(
                 DiscountType::FractionWithMaximum, "20", std::nullopt,
                 std::nullopt,
                 CustomPromoInfo{"test_discount2", "discount2 for test",
                                 "http://test_promo2.jpeg"},
                 "124")),
             impl::kOwn}},  // matched_discounts
        {
            "2",         // public_id
            Money(200),  // price
            Money(70),   // promo_price
            {{impl::kMoneyTypeId, impl::kMoneyTypeName,
              "http://test_promo.jpeg", std::nullopt},
             {impl::kMoneyTypeId, impl::kMoneyTypeName,
              "http://test_promo2.jpeg", std::nullopt}},  // discount_promos
            std::nullopt,                                 // cashback_promo
            {}                                            // options
        },                                                // item_with_discount
        "fraction_and_absolute_discounts",
    },
    // тест на процентную и продуктовую скидку
    {
        {
            "2",         // public_id
            Money(200),  // price
            Money(150),  // promo_price
            {},          // promo_types_in
            {}           // options
        },               // item
        {DiscountApplier::Discount{
             MakeDiscount(MakeV2MenuDiscount(
                 DiscountType::FractionWithMaximum, "50", std::nullopt,
                 std::nullopt,
                 CustomPromoInfo{"test_discount2", "discount2 for test",
                                 "http://test_promo2.jpeg"},
                 "124")),
             impl::kPlace},
         DiscountApplier::Discount{
             MakeDiscount(MakeV2MenuDiscount(DiscountType::ProductValue)),
             impl::kOwn}},  // matched_discounts
        {
            "2",         // public_id
            Money(200),  // price
            Money(75),   // promo_price
            {{impl::kMoneyTypeId, impl::kMoneyTypeName,
              "http://test_promo2.jpeg", std::nullopt}},  // discount_promos
            std::nullopt,                                 // cashback_promo
            {}                                            // options
        },                                                // item_with_discount
        "money_and_product_discounts",
    },
    // тест на продуктовую скидку
    {
        {
            "2",           // public_id
            Money(200),    // price
            std::nullopt,  // promo_price
            {},            // promo_types_in
            {}             // options
        },                 // item
        {DiscountApplier::Discount{
             MakeDiscount(MakeV2MenuDiscount(DiscountType::ProductValue)),
             impl::kPlace},
         DiscountApplier::Discount{
             MakeDiscount(MakeV2MenuDiscount(DiscountType::ProductValue)),
             impl::kOwn}},  // matched_discounts
        {
            "2",           // public_id
            Money(200),    // price
            std::nullopt,  // promo_price
            {{impl::kProductTypeId, impl::kProductTypeName, "picture_uri",
              std::nullopt}},  // discount_promos
            std::nullopt,      // cashback_promo
            {}                 // options
        },                     // item_with_discount
        "product_discounts",
    },
    // тест на продуктовую скидку
    {
        {
            "2",           // public_id
            Money(200),    // price
            std::nullopt,  // promo_price
            {},            // promo_types_in
            {}             // options
        },                 // item
        {DiscountApplier::Discount{
             MakeDiscount(MakeV2MenuDiscount(DiscountType::ProductValue)),
             impl::kPlace},
         DiscountApplier::Discount{
             MakeDiscount(MakeV2MenuDiscount(
                 DiscountType::FractionWithMaximum, "50", std::nullopt,
                 std::nullopt,
                 CustomPromoInfo{"test_discount2", "discount2 for test",
                                 "http://test_promo2.jpeg"},
                 "124")),
             impl::kOwn}},  // matched_discounts
        {
            "2",           // public_id
            Money(200),    // price
            std::nullopt,  // promo_price
            {{impl::kProductTypeId, impl::kProductTypeName, "picture_uri",
              std::nullopt}},  // discount_promos
            std::nullopt,      // cashback_promo
            {}                 // options
        },                     // item_with_discount
        "product_and_money_discounts",
    }};

TEST_P(TestApplyMenuDiscounts, BasicTest) {
  const auto params = GetParam();
  DiscountApplier discount_applier{params.matched_discounts};
  auto result = discount_applier.Apply(params.item);

  ASSERT_EQ(result.public_id, params.item_with_discount.public_id);
  ASSERT_EQ(result.price, params.item_with_discount.price);
  ASSERT_EQ(result.promo_price.has_value(),
            params.item_with_discount.promo_price.has_value());
  if (result.promo_price.has_value()) {
    ASSERT_EQ(result.promo_price.value(),
              params.item_with_discount.promo_price.value());
  }
  ASSERT_EQ(result.discount_promos.size(),
            params.item_with_discount.discount_promos.size());
  for (uint i = 0; i < params.item_with_discount.discount_promos.size(); i++) {
    ASSERT_EQ(result.discount_promos[i].id,
              params.item_with_discount.discount_promos[i].id);
    ASSERT_EQ(result.discount_promos[i].name,
              params.item_with_discount.discount_promos[i].name);
    ASSERT_EQ(result.discount_promos[i].picture_uri,
              params.item_with_discount.discount_promos[i].picture_uri);
    ASSERT_EQ(
        result.discount_promos[i].detailed_picture_url,
        params.item_with_discount.discount_promos[i].detailed_picture_url);
  }
  // ASSERT_EQ(result.cashback_promo, params.item_with_discount.cashback_promo);
  ASSERT_EQ(result.options.size(), params.item_with_discount.options.size());
  for (uint i = 0; i < params.item_with_discount.options.size(); i++) {
    ASSERT_EQ(result.options[i].id, params.item_with_discount.options[i].id);
    ASSERT_EQ(result.options[i].price,
              params.item_with_discount.options[i].price);
    ASSERT_EQ(result.options[i].promo_price,
              params.item_with_discount.options[i].promo_price);
  }
}

INSTANTIATE_TEST_SUITE_P(/* no prefix */, TestApplyMenuDiscounts,
                         testing::ValuesIn(kBasicTestParams),
                         testing::PrintToStringParamName());

}  // namespace apply_menu_discounts

}  // namespace eats_discounts_applicator::tests
