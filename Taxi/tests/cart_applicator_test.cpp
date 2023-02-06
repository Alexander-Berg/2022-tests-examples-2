#include <gtest/gtest.h>

#include <applicators/cart.hpp>
#include <eats-discounts-applicator/common.hpp>
#include <requesters/utils.hpp>
#include <tests/utils.hpp>
#include <validators.hpp>

#include <experiments3.hpp>
#include "eats-discounts-applicator/discounts_threshold.hpp"

namespace eats_discounts_applicator::tests {

namespace {

struct TestParams {
  CartForDiscount cart;
  requesters::MatchedDiscounts discounts_response;
  CartWithDiscount exp_cart;
  std::string test_name;
};

class TestCartApplicator : public testing::TestWithParam<TestParams> {};

std::string PrintToString(const TestParams& params) { return params.test_name; }

const std::vector<TableData> kTableMoneyData = {
    TableData{DiscountType::AbsoluteValue /*type*/, "500" /*from cost*/,
              "15" /*value*/},
    TableData{DiscountType::FractionWithMaximum /*type*/, "1000" /*from cost*/,
              "10" /*value*/},
};

const std::vector<TableData> kTableProductData = {
    TableData{DiscountType::ProductValue /*type*/, "1500" /*from cost*/,
              "787" /*value*/},
};

const std::vector<TableData> kTablecombineData = {
    TableData{DiscountType::ProductValue /*type*/, "1000" /*from cost*/,
              "787" /*value*/},
    TableData{DiscountType::FractionWithMaximum /*type*/, "1000" /*from cost*/,
              "10" /*value*/},
};

const std::vector<TestParams> kBasicTestParams = {
    {
        {{{1, "1", Money(100), std::nullopt, 1, {}, std::nullopt}}, kZeroMoney},
        MakeResponses(DiscountType::NoDiscount, kEmptyExcludedInformation,
                      kPromoTypesInfo),
        {{{1, "1", Money(100), 1, {}, {}}},
         {},
         {},
         {},
         Money(100),
         {std::nullopt, std::nullopt, std::nullopt},
         {}},
        "no_discounts",
    },
    {
        {{{1, "1", Money(100), Money(40), 1, {}, std::nullopt}}, kZeroMoney},
        MakeResponses(DiscountType::NoDiscount, kEmptyExcludedInformation,
                      kPromoTypesInfo),
        {{{1, "1", Money(100), 1, {}, {}}},
         {},
         {},
         {},
         Money(40),
         {std::nullopt, std::nullopt, std::nullopt},
         {}},
        "no_discounts_with_promo",
    },
    {
        {{{2, "1", Money(100), std::nullopt, 1, {}, std::nullopt}}, kZeroMoney},
        MakeResponses(DiscountType::AbsoluteValue, kEmptyExcludedInformation,
                      kPromoTypesInfo, "10"),
        {{{2,
           "1",
           Money(100),
           1,
           {},
           {BasicPromoType{21, std::to_string(impl::kMoneyTypeId), "name",
                           "descr", "picture_uri", Money(10), impl::kOwn}}}},
         {},
         {},
         {},
         Money(90),
         {std::nullopt, std::nullopt, std::nullopt},
         {}},
        "absolute_discounts",
    },
    {
        {{{2, "1", Money(100), std::nullopt, 1, {}, std::nullopt}}, kZeroMoney},
        requesters::ParseMatchResponse(
            {MakeRestaurantMenuDiscountResponse(
                DiscountType::AbsoluteValue, "10", std::nullopt, std::nullopt,
                std::nullopt, "one")},
            experiments::ExcludedInformation{{"two", "three"},
                                             kEmptyExcludedDiscounts},
            {{"one", {"name", "descr", "pict"}}}),
        {{{2,
           "1",
           Money(100),
           1,
           {},
           {BasicPromoType{21, std::to_string(impl::kMoneyTypeId), "name",
                           "descr", "picture_uri", Money(10), impl::kPlace}}}},
         {},
         {},
         {},
         Money(90),
         {std::nullopt, std::nullopt, std::nullopt},
         {}},
        "not_exclude_discounts_restaurant_menu_by_promo",
    },
    {
        {{{5, "1", Money(1000), std::nullopt, 1, {}, std::nullopt}},
         kZeroMoney},
        requesters::ParseMatchResponse(
            {MakeRestaurantMenuDiscountResponse(
                DiscountType::FractionWithMaximum, "20", "150", std::nullopt,
                std::nullopt, "one")},
            experiments::ExcludedInformation{{"one", "two"},
                                             kEmptyExcludedDiscounts},
            {{"one", {"name", "descr", "pict"}}}),
        {{{5, "1", Money(1000), 1, {}, {}}},
         {},
         {},
         {},
         Money(1000),
         {std::nullopt, std::nullopt, std::nullopt},
         {}},
        "exclude_discounts_restaurant_menu_by_promo",
    },
    {
        {{{2, "1", Money(100), std::nullopt, 1, {}, std::nullopt}}, kZeroMoney},
        MakeResponses(DiscountType::AbsoluteValue,
                      experiments::ExcludedInformation{{"two", "three"},
                                                       kEmptyExcludedDiscounts},
                      {{"one", {"name", "descr", "pict"}}}, "10", std::nullopt,
                      std::nullopt, "one"),
        {{{2,
           "1",
           Money(100),
           1,
           {},
           {BasicPromoType{21, std::to_string(impl::kMoneyTypeId), "name",
                           "descr", "picture_uri", Money(10), impl::kOwn}}}},
         {},
         {},
         {},
         Money(90),
         {std::nullopt, std::nullopt, std::nullopt},
         {}},
        "not_exclude_menu_discounts",
    },
    {
        {{{2, "1", Money(100), std::nullopt, 1, {}, std::nullopt}}, kZeroMoney},
        MakeResponses(DiscountType::AbsoluteValue,
                      experiments::ExcludedInformation{{"two", "one"},
                                                       kEmptyExcludedDiscounts},
                      {{"two", {"name", "descr", "pict"}}}, "10", std::nullopt,
                      std::nullopt, "two"),
        {{{2, "1", Money(100), 1, {}, {}}},
         {},
         {},
         {},
         Money(100),
         {std::nullopt, std::nullopt, std::nullopt},
         {}},
        "exclude_menu_discounts",
    },
    {
        {{{2, "1", Money(100), std::nullopt, 1, {}, std::nullopt}}, kZeroMoney},
        requesters::ParseMatchResponse({MakeRestaurantMenuDiscountResponse(
                                           DiscountType::AbsoluteValue, "10")},
                                       kEmptyExcludedInformation,
                                       kPromoTypesInfo),
        {{{2,
           "1",
           Money(100),
           1,
           {},
           {BasicPromoType{21, std::to_string(impl::kMoneyTypeId), "name",
                           "descr", "picture_uri", Money(10), impl::kPlace}}}},
         {},
         {},
         {},
         Money(90),
         {std::nullopt, std::nullopt, std::nullopt},
         {}},
        "absolute_rest_discounts",
    },
    {
        {{{2, "1", Money(100), Money(90), 1, {}, std::nullopt}}, kZeroMoney},
        MakeResponses(DiscountType::AbsoluteValue, kEmptyExcludedInformation,
                      kPromoTypesInfo, "10"),
        {{{2,
           "1",
           Money(100),
           1,
           {},
           {BasicPromoType{21, std::to_string(impl::kMoneyTypeId), "name",
                           "descr", "picture_uri", Money(10), impl::kOwn}}}},
         {},
         {},
         {},
         Money(80),
         {std::nullopt, std::nullopt, std::nullopt},
         {}},
        "absolute_discounts_with_promo",
    },
    {
        {{{3, "1", Money(100), std::nullopt, 1, {}, std::nullopt}}, kZeroMoney},
        requesters::ParseMatchResponse(
            std::vector<discounts_client::V2MatchDiscountsResponse>(),
            experiments::ExcludedInformation{{"one", "two"},
                                             kEmptyExcludedDiscounts},
            kPromoTypesInfo),
        {{{3, "1", Money(100), 1, {}, {}}},
         {},
         {},
         {},
         Money(100),
         {std::nullopt, std::nullopt, std::nullopt},
         {}},
        "empty_discounts_response",
    },
    {
        {{{4, "1", Money(1000), std::nullopt, 2, {}, std::nullopt}},
         kZeroMoney},
        MakeResponses(DiscountType::FractionWithMaximum,
                      kEmptyExcludedInformation, kPromoTypesInfo, "10"),
        {{{4,
           "1",
           Money(1000),
           2,
           {},
           {BasicPromoType{21, std::to_string(impl::kMoneyTypeId), "name",
                           "descr", "picture_uri", Money(100), impl::kOwn}}}},
         {},
         {},
         {},
         Money(1800),
         {std::nullopt, std::nullopt, std::nullopt},
         {}},
        "fraction_with_max_discounts_no_max",
    },
    {
        {{{4, "1", Money(1000), std::nullopt, 2, {}, std::nullopt}},
         kZeroMoney},
        requesters::ParseMatchResponse(
            {MakeRestaurantMenuDiscountResponse(
                DiscountType::FractionWithMaximum, "10")},
            kEmptyExcludedInformation, kPromoTypesInfo),
        {{{4,
           "1",
           Money(1000),
           2,
           {},
           {BasicPromoType{21, std::to_string(impl::kMoneyTypeId), "name",
                           "descr", "picture_uri", Money(100), impl::kPlace}}}},
         {},
         {},
         {},
         Money(1800),
         {std::nullopt, std::nullopt, std::nullopt},
         {}},
        "fraction_with_max_rest_discounts_no_max",
    },
    {
        {{{5, "1", Money(1000), std::nullopt, 1, {}, std::nullopt}},
         kZeroMoney},
        MakeResponses(DiscountType::FractionWithMaximum,
                      kEmptyExcludedInformation, kPromoTypesInfo, "20", "150"),
        {{{5,
           "1",
           Money(1000),
           1,
           {},
           {BasicPromoType{21, std::to_string(impl::kMoneyTypeId), "name",
                           "descr", "picture_uri", Money(150), impl::kOwn}}}},
         {},
         {},
         {},
         Money(850),
         {std::nullopt, std::nullopt, std::nullopt},
         {}},
        "fraction_with_max_discounts",
    },
    {
        {{{5, "1", Money(1000), std::nullopt, 1, {}, std::nullopt}},
         kZeroMoney},
        requesters::ParseMatchResponse(
            {MakeRestaurantMenuDiscountResponse(
                DiscountType::FractionWithMaximum, "20", "150")},
            kEmptyExcludedInformation, kPromoTypesInfo),
        {{{5,
           "1",
           Money(1000),
           1,
           {},
           {BasicPromoType{21, std::to_string(impl::kMoneyTypeId), "name",
                           "descr", "picture_uri", Money(150), impl::kPlace}}}},
         {},
         {},
         {},
         Money(850),
         {std::nullopt, std::nullopt, std::nullopt},
         {}},
        "fraction_with_max_rest_discounts",
    },
    {
        {{{2, "1", Money(200), Money(150), 1, {}, std::nullopt}}, kZeroMoney},
        MakeResponses(DiscountType::FractionWithMaximum,
                      kEmptyExcludedInformation, kPromoTypesInfo, "10"),
        {{{2,
           "1",
           Money(200),
           1,
           {},
           {BasicPromoType{21, std::to_string(impl::kMoneyTypeId), "name",
                           "descr", "picture_uri", Money(15), impl::kOwn}}}},
         {},
         {},
         {},
         Money(135),
         {std::nullopt, std::nullopt, std::nullopt},
         {}},
        "fraction_discounts_with_promo",
    },
    {
        {{{3, "1", Money(150), std::nullopt, 1, {}, std::nullopt}}, kZeroMoney},
        MakeResponses(DiscountType::TableValue, kEmptyExcludedInformation,
                      kPromoTypesInfo),
        {{{3, "1", Money(150), 1, {}, {}}},
         {},
         {},
         {},
         Money(150),
         {std::nullopt, std::nullopt, std::nullopt},
         {}},
        "table_discounts_discount",
    },
    {
        {{{1, "1", Money(500), std::nullopt, 1, {}, std::nullopt}}, kZeroMoney},
        MakeResponses(DiscountType::ProductValue, kEmptyExcludedInformation,
                      kPromoTypesInfo, "100", std::nullopt /*max_value*/,
                      3 /* bundle */),
        {{{1, "1", Money(500), 1, {}, {}}},
         {},
         {},
         {},
         Money(500),
         {std::nullopt, std::nullopt, std::nullopt},
         {}},
        "product_discount_not_enough",
    },
    {
        {{{1, "1", Money(500), std::nullopt, 3, {}, std::nullopt}}, kZeroMoney},
        MakeResponses(DiscountType::ProductValue, kEmptyExcludedInformation,
                      kPromoTypesInfo, "100", std::nullopt /*max_value*/,
                      3 /* bundle */),
        {{{1, "1", Money(500), 2, {}, {}}},
         {
             {"1",
              Money(500),
              1,
              {},
              {BasicPromoType{21, std::to_string(impl::kProductTypeId), "name",
                              "descr", "picture_uri", Money(500), impl::kOwn}}},
         },
         {},
         {},
         Money(1000),
         {std::nullopt, std::nullopt, std::nullopt},
         {}},
        "product_discount_one_item_to_add",
    },
    {
        {{{1, "1", Money(500), std::nullopt, 3, {}, std::nullopt}}, kZeroMoney},
        requesters::ParseMatchResponse(
            {MakeRestaurantMenuDiscountResponse(
                DiscountType::ProductValue, "100", std::nullopt /*max_value*/,
                3 /* bundle */)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        {{{1, "1", Money(500), 2, {}, {}}},
         {
             {"1",
              Money(500),
              1,
              {},
              {BasicPromoType{21, std::to_string(impl::kProductTypeId), "name",
                              "descr", "picture_uri", Money(500),
                              impl::kPlace}}},
         },
         {},
         {},
         Money(1000),
         {std::nullopt, std::nullopt, std::nullopt},
         {}},
        "product_rest_discount_one_item_to_add",
    },
    {
        {{{1, "1", Money(500), std::nullopt, 4, {}, std::nullopt}}, kZeroMoney},
        MakeResponses(DiscountType::ProductValue, kEmptyExcludedInformation,
                      kPromoTypesInfo, "100", std::nullopt /*max_value*/,
                      2 /* bundle */),
        {{{1, "1", Money(500), 2, {}, {}}},
         {
             {"1",
              Money(500),
              2,
              {},
              {BasicPromoType{21, std::to_string(impl::kProductTypeId), "name",
                              "descr", "picture_uri", Money(500), impl::kOwn}}},
         },
         {},
         {},
         Money(1000),
         {std::nullopt, std::nullopt, std::nullopt},
         {}},
        "product_discount_two_items_to_add",
    },
    {
        {{{1, "1", Money(500), std::nullopt, 4, {}, std::nullopt}}, kZeroMoney},
        requesters::ParseMatchResponse(
            {MakeRestaurantMenuDiscountResponse(
                DiscountType::ProductValue, "100", std::nullopt /*max_value*/,
                2 /* bundle */)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        {{{1, "1", Money(500), 2, {}, {}}},
         {
             {"1",
              Money(500),
              2,
              {},
              {BasicPromoType{21, std::to_string(impl::kProductTypeId), "name",
                              "descr", "picture_uri", Money(500),
                              impl::kPlace}}},
         },
         {},
         {},
         Money(1000),
         {std::nullopt, std::nullopt, std::nullopt},
         {}},
        "product_rest_discount_two_items_to_add",
    },
    {
        {{{2, "1", Money(100), std::nullopt, 1, {}, std::nullopt}}, kZeroMoney},
        requesters::ParseMatchResponse(
            {MakeRestaurantMenuDiscountResponse(DiscountType::AbsoluteValue,
                                                "10"),
             MakeMenuDiscountResponse(DiscountType::AbsoluteValue, "10")},
            kEmptyExcludedInformation, kPromoTypesInfo),
        {{{2,
           "1",
           Money(100),
           1,
           {},
           {BasicPromoType{21, std::to_string(impl::kMoneyTypeId), "name",
                           "descr", "picture_uri", Money(10), impl::kPlace},
            BasicPromoType{21, std::to_string(impl::kMoneyTypeId), "name",
                           "descr", "picture_uri", Money(10), impl::kOwn}}}},
         {},
         {},
         {},
         Money(80),
         {std::nullopt, std::nullopt, std::nullopt},
         {}},
        "prefer_place_discounts",
    },
    {
        {{{2, "1", Money(100), std::nullopt, 1, {}, std::nullopt}}, kZeroMoney},
        MakeResponses(DiscountType::AbsoluteValue,
                      experiments::ExcludedInformation{
                          {}, {ExpDiscountType::kYandexMenuMoneyDiscount}},
                      kPromoTypesInfo, "10"),
        {{{2, "1", Money(100), 1, {}, {}}},
         {},
         {},
         {},
         Money(100),
         {std::nullopt, std::nullopt, std::nullopt},
         {}},
        "money_discount_disable_by_exp",
    },
    {
        {{{1, "1", Money(500), std::nullopt, 3, {}, std::nullopt}}, kZeroMoney},
        MakeResponses(DiscountType::ProductValue,
                      experiments::ExcludedInformation{
                          {}, {ExpDiscountType::kYandexMenuProductDiscount}},
                      kPromoTypesInfo, "100", std::nullopt /*max_value*/,
                      3 /* bundle */),
        {{{1, "1", Money(500), 3, {}, {}}},
         {},
         {},
         {},
         Money(1500),
         {std::nullopt, std::nullopt, std::nullopt},
         {}},
        "product_discount_disable_by_exp",
    },
    {
        {{{5, "1", Money(300), std::nullopt, 1, {}, std::nullopt}}, Money(300)},
        requesters::ParseMatchResponse(
            {MakeDiscountCartResponse(kTableMoneyData)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        {{{5, "1", Money(300), 1, {}, {}}},
         {},
         {},
         {},
         Money(300),
         {std::nullopt, std::nullopt, std::nullopt},
         {DiscountThreshold{Money(500), DiscountTypeForThreshold::kDiscount,
                            ValueType::kAbsolute, Money(15), std::nullopt, 0},
          DiscountThreshold{Money(1000), DiscountTypeForThreshold::kDiscount,
                            ValueType::kFraction, Money(10), std::nullopt, 0}}},
        "cart_discount_no_discount",
    },
    {
        {{{5, "1", Money(900), std::nullopt, 1, {}, std::nullopt}}, Money(900)},
        requesters::ParseMatchResponse(
            {MakeDiscountCartResponse(kTableMoneyData)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        {{{5, "1", Money(900), 1, {}, {}}},
         {},
         {BasicPromoType{
             std::stoi(kRestaurantCartDiscountId),
             std::to_string(impl::kCartMoneyTypeId),
             kRestaurantCartDiscountName, kRestaurantCartDiscountDescription,
             kRestaurantCartDiscountPictureUri, Money(15), impl::kPlace}},
         {},
         Money(885),
         {std::nullopt, std::nullopt, std::nullopt},
         {DiscountThreshold{Money(500), DiscountTypeForThreshold::kDiscount,
                            ValueType::kAbsolute, Money(15), std::nullopt, 0},
          DiscountThreshold{Money(1000), DiscountTypeForThreshold::kDiscount,
                            ValueType::kFraction, Money(10), std::nullopt, 0}}},
        "cart_discount_absolute",
    },
    {
        {{{5, "1", Money(1000), std::nullopt, 1, {}, std::nullopt}},
         Money(1000)},
        requesters::ParseMatchResponse(
            {MakeDiscountCartResponse(kTableMoneyData)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        {{{5, "1", Money(1000), 1, {}, {}}},
         {},
         {BasicPromoType{
             std::stoi(kRestaurantCartDiscountId),
             std::to_string(impl::kCartMoneyTypeId),
             kRestaurantCartDiscountName, kRestaurantCartDiscountDescription,
             kRestaurantCartDiscountPictureUri, Money(100), impl::kPlace}},
         {},
         Money(900),
         {std::nullopt, std::nullopt, std::nullopt},
         {DiscountThreshold{Money(500), DiscountTypeForThreshold::kDiscount,
                            ValueType::kAbsolute, Money(15), std::nullopt, 0},
          DiscountThreshold{Money(1000), DiscountTypeForThreshold::kDiscount,
                            ValueType::kFraction, Money(10), std::nullopt, 0}}},
        "cart_discount_fraction",
    },
    {
        {{{5, "1", Money(1000), std::nullopt, 1, {}, std::nullopt}},
         Money(1000)},
        requesters::ParseMatchResponse(
            {MakeDiscountCartResponse(kTableProductData)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        {{{5, "1", Money(1000), 1, {}, {}}},
         {},
         {},
         {},
         Money(1000),
         {std::nullopt, std::nullopt, std::nullopt},
         {DiscountThreshold{Money(1500), DiscountTypeForThreshold::kGift,
                            ValueType::kOther, Money(100), std::nullopt, 0}}},
        "cart_discount_no_new_item",
    },
    {
        {{{5, "1", Money(1500), std::nullopt, 1, {}, std::nullopt}},
         Money(1500)},
        requesters::ParseMatchResponse(
            {MakeDiscountCartResponse(kTableProductData)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        {{{5, "1", Money(1500), 1, {}, {}}},
         {},
         {},
         {{"787", 1,
           PromoTypeInfo{std::stoi(kRestaurantCartDiscountId),
                         std::to_string(impl::kGiftProductForCartTypeId),
                         kRestaurantCartDiscountName,
                         kRestaurantCartDiscountDescription,
                         kRestaurantCartDiscountPictureUri, impl::kPlace}}},
         Money(1500),
         {std::nullopt, std::nullopt, std::nullopt},
         {DiscountThreshold{Money(1500), DiscountTypeForThreshold::kGift,
                            ValueType::kOther, Money(100), std::nullopt, 0}}},
        "cart_discount_add_new_item",
    },
    {
        {{{5, "1", Money(1000), std::nullopt, 1, {}, std::nullopt}},
         Money(1000)},
        requesters::ParseMatchResponse(
            {MakeDiscountCartResponse(kTablecombineData)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        {{{5, "1", Money(1000), 1, {}, {}}},
         {},
         {BasicPromoType{
             std::stoi(kRestaurantCartDiscountId),
             std::to_string(impl::kCartMoneyTypeId),
             kRestaurantCartDiscountName, kRestaurantCartDiscountDescription,
             kRestaurantCartDiscountPictureUri, Money(100), impl::kPlace}},
         {{"787", 1,
           PromoTypeInfo{std::stoi(kRestaurantCartDiscountId),
                         std::to_string(impl::kGiftProductForCartTypeId),
                         kRestaurantCartDiscountName,
                         kRestaurantCartDiscountDescription,
                         kRestaurantCartDiscountPictureUri, impl::kPlace}}},
         Money(900),
         {std::nullopt, std::nullopt, std::nullopt},
         {DiscountThreshold{Money(1000), DiscountTypeForThreshold::kDiscount,
                            ValueType::kFraction, Money(10), std::nullopt, 0},
          DiscountThreshold{Money(1000), DiscountTypeForThreshold::kGift,
                            ValueType::kOther, Money(100), std::nullopt, 0}}},
        "combine_cart_discount",
    },
};

template <class Item>
void CheckItem(const Item& item, const Item& exp_item) {
  EXPECT_EQ(item.public_id, exp_item.public_id);
  EXPECT_EQ(item.price, exp_item.price);
  EXPECT_EQ(item.quantity, exp_item.quantity);
}

template <class Promo>
void CheckPromoTypeInfo(const Promo& promo, const Promo& exp_promo) {
  EXPECT_EQ(promo.id, exp_promo.id);
  EXPECT_EQ(promo.type_id, exp_promo.type_id);
  EXPECT_EQ(promo.name, exp_promo.name);
  EXPECT_EQ(promo.description, exp_promo.description);
  EXPECT_EQ(promo.provider, exp_promo.provider);
  EXPECT_EQ(promo.picture_uri, exp_promo.picture_uri);
}

void CheckDiscountThreshold(const DiscountThreshold& disc,
                            const DiscountThreshold& exp_disc) {
  EXPECT_EQ(disc.from_cost, exp_disc.from_cost);
  EXPECT_EQ(disc.discount_type, exp_disc.discount_type);
  EXPECT_EQ(disc.value, exp_disc.value);
  EXPECT_EQ(disc.amount, exp_disc.amount);
  EXPECT_EQ(disc.max_amount, exp_disc.max_amount);
}

}  // namespace

TEST_P(TestCartApplicator, BasicTest) {
  const auto params = GetParam();
  auto cur_cart = params.cart;
  cur_cart.DeleteDiscountItems();
  auto cart_result = applicators::ApplyDiscountsForCart(
      cur_cart, ApplyDiscountsForCartSettings{}, params.discounts_response);

  EXPECT_EQ(cart_result.items.size(), params.exp_cart.items.size());
  int i = 0;
  for (const auto& item : cart_result.items) {
    const auto& it = params.exp_cart.items[i++];
    EXPECT_EQ(item.id, it.id);
    EXPECT_EQ(item.promos.size(), it.promos.size());
    for (uint i = 0; i < item.promos.size(); i++) {
      CheckPromoTypeInfo(item.promos[i], it.promos[i]);
      EXPECT_EQ(item.promos[i].amount, it.promos[i].amount);
    }
    CheckItem(item, it);
  }
  i = 0;
  for (const auto& item : cart_result.new_items) {
    const auto& it = params.exp_cart.new_items[i++];
    CheckPromoTypeInfo(item.promo, it.promo);
    EXPECT_EQ(item.promo.amount, it.promo.amount);
    CheckItem(item, it);
  }
  EXPECT_EQ(cart_result.total, params.exp_cart.total);

  EXPECT_EQ(cart_result.cart_discounts.size(),
            params.exp_cart.cart_discounts.size());

  i = 0;
  for (const auto& cart_discount : cart_result.cart_discounts) {
    const auto& exp_discount = params.exp_cart.cart_discounts[i++];
    CheckPromoTypeInfo(cart_discount, exp_discount);
    EXPECT_EQ(cart_discount.amount, exp_discount.amount);
  }

  EXPECT_EQ(cart_result.new_items_from_cart_discounts.size(),
            params.exp_cart.new_items_from_cart_discounts.size());

  i = 0;
  for (const auto& new_item : cart_result.new_items_from_cart_discounts) {
    const auto& exp_new_item =
        params.exp_cart.new_items_from_cart_discounts[i++];
    EXPECT_EQ(new_item.item_id, exp_new_item.item_id);
    EXPECT_EQ(new_item.quantity, exp_new_item.quantity);
    CheckPromoTypeInfo(new_item.promo, exp_new_item.promo);
  }

  EXPECT_EQ(cart_result.discount_thresholds.size(),
            params.exp_cart.discount_thresholds.size());
  i = 0;
  for (const auto& discount : cart_result.discount_thresholds) {
    CheckDiscountThreshold(discount, params.exp_cart.discount_thresholds[i++]);
  }
}

INSTANTIATE_TEST_SUITE_P(/* no prefix */, TestCartApplicator,
                         testing::ValuesIn(kBasicTestParams),
                         testing::PrintToStringParamName());

}  // namespace eats_discounts_applicator::tests
