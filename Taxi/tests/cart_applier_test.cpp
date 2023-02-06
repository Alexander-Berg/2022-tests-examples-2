#include <gtest/gtest.h>

#include <applicators/cart_applier.hpp>
#include <eats-discounts-applicator/common.hpp>
#include <requesters/utils.hpp>
#include <tests/utils.hpp>
#include <validators.hpp>

#include <experiments3.hpp>

namespace eats_discounts_applicator::tests {

namespace {

struct TestParams {
  requesters::MatchedDiscounts discounts_response;
  Money cart_subtotal;
  std::vector<BasicPromoType> exp_cart_discounts;
  std::vector<NewItemCartDiscount> exp_new_items;
  std::string test_name;
};

class TestCartDiscountsApplier : public testing::TestWithParam<TestParams> {};

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
    {
        requesters::ParseMatchResponse(
            {MakeDiscountCartResponse(kTableMoneyData)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        Money(100),
        {},
        {},
        "restaurant_no_cart_discount",
    },
    {
        requesters::ParseMatchResponse(
            {MakeDiscountCartResponse(kTableMoneyData,
                                      std::nullopt /*promo_type*/,
                                      CartDiscount::YandexDiscount)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        Money(100),
        {},
        {},
        "yandex_no_cart_discount",
    },
    {
        requesters::ParseMatchResponse(
            {MakeDiscountCartResponse(kTableMoneyData)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        Money(500),
        {BasicPromoType{
            std::stoll(kRestaurantCartDiscountId),
            std::to_string(impl::kCartMoneyTypeId), kRestaurantCartDiscountName,
            kRestaurantCartDiscountDescription,
            kRestaurantCartDiscountPictureUri, Money(15), impl::kPlace}},
        {},
        "restaurant_cart_discount",
    },
    {
        requesters::ParseMatchResponse(
            {MakeDiscountCartResponse(kTableMoneyData,
                                      std::nullopt /*promo_type*/,
                                      CartDiscount::YandexDiscount)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        Money(500),
        {BasicPromoType{std::stoll(kYandexCartDiscountId),
                        std::to_string(impl::kCartMoneyTypeId),
                        kYandexCartDiscountName, kYandexCartDiscountDescription,
                        kYandexCartDiscountPictureUri, Money(15), impl::kOwn}},
        {},
        "yandex_cart_discount",
    },
    {
        requesters::ParseMatchResponse(
            {MakeDiscountCartResponse(kTableMoneyData,
                                      std::nullopt /*promo_type*/,
                                      CartDiscount::CofinancingDiscount)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        Money(500),
        {BasicPromoType{
             std::stoll(kRestaurantCartDiscountId),
             std::to_string(impl::kCartMoneyTypeId),
             kRestaurantCartDiscountName, kRestaurantCartDiscountDescription,
             kRestaurantCartDiscountPictureUri, Money(15), impl::kPlace},
         BasicPromoType{std::stoll(kYandexCartDiscountId),
                        std::to_string(impl::kCartMoneyTypeId),
                        kYandexCartDiscountName, kYandexCartDiscountDescription,
                        kYandexCartDiscountPictureUri, Money(15), impl::kOwn}},
        {},
        "cofinancing_cart_discount",
    },
    {
        requesters::ParseMatchResponse(
            {MakeDiscountCartResponse(kTableMoneyData,
                                      std::nullopt /*promo_type*/,
                                      CartDiscount::CofinancingDiscount)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        Money(1000),
        {BasicPromoType{
             std::stoll(kRestaurantCartDiscountId),
             std::to_string(impl::kCartMoneyTypeId),
             kRestaurantCartDiscountName, kRestaurantCartDiscountDescription,
             kRestaurantCartDiscountPictureUri, Money(600), impl::kPlace},
         BasicPromoType{std::stoll(kYandexCartDiscountId),
                        std::to_string(impl::kCartMoneyTypeId),
                        kYandexCartDiscountName, kYandexCartDiscountDescription,
                        kYandexCartDiscountPictureUri, Money(400), impl::kOwn}},
        {},
        "over_cofinancing_cart_discount",
    },
    {
        requesters::ParseMatchResponse(
            {MakeDiscountCartResponse(kTableCombineData)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        Money(1000),
        {BasicPromoType{
            std::stoll(kRestaurantCartDiscountId),
            std::to_string(impl::kCartMoneyTypeId), kRestaurantCartDiscountName,
            kRestaurantCartDiscountDescription,
            kRestaurantCartDiscountPictureUri, Money(100), impl::kPlace}},

        {{"787" /* item_id */, 1 /* quantity */,
          PromoTypeInfo{std::stoll(kRestaurantCartDiscountId),
                        std::to_string(impl::kGiftProductForCartTypeId),
                        kRestaurantCartDiscountName,
                        kRestaurantCartDiscountDescription,
                        kRestaurantCartDiscountPictureUri, impl::kPlace}}},
        "restaurant_product_cart_discount",
    },
    {
        requesters::ParseMatchResponse(
            {MakeDiscountCartResponse(kTableCombineData,
                                      std::nullopt /*promo_type*/,
                                      CartDiscount::YandexDiscount)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        Money(1000),
        {BasicPromoType{std::stoll(kYandexCartDiscountId),
                        std::to_string(impl::kCartMoneyTypeId),
                        kYandexCartDiscountName, kYandexCartDiscountDescription,
                        kYandexCartDiscountPictureUri, Money(100), impl::kOwn}},
        {{"787" /* item_id */, 1 /* quantity */,
          PromoTypeInfo{std::stoll(kYandexCartDiscountId),
                        std::to_string(impl::kGiftProductForCartTypeId),
                        kYandexCartDiscountName, kYandexCartDiscountDescription,
                        kYandexCartDiscountPictureUri, impl::kOwn}}},
        "yandex_product_cart_discount",
    },
    {
        requesters::ParseMatchResponse(
            {MakeDiscountCartResponse(kTableCombineData,
                                      std::nullopt /*promo_type*/,
                                      CartDiscount::CofinancingDiscount)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        Money(1000),
        {BasicPromoType{
             std::stoll(kRestaurantCartDiscountId),
             std::to_string(impl::kCartMoneyTypeId),
             kRestaurantCartDiscountName, kRestaurantCartDiscountDescription,
             kRestaurantCartDiscountPictureUri, Money(100), impl::kPlace},
         BasicPromoType{std::stoll(kYandexCartDiscountId),
                        std::to_string(impl::kCartMoneyTypeId),
                        kYandexCartDiscountName, kYandexCartDiscountDescription,
                        kYandexCartDiscountPictureUri, Money(100), impl::kOwn}},
        {{"787" /* item_id */, 1 /* quantity */,
          PromoTypeInfo{std::stoll(kRestaurantCartDiscountId),
                        std::to_string(impl::kGiftProductForCartTypeId),
                        kRestaurantCartDiscountName,
                        kRestaurantCartDiscountDescription,
                        kRestaurantCartDiscountPictureUri, impl::kPlace}},
         {"787" /* item_id */, 1 /* quantity */,
          PromoTypeInfo{std::stoll(kYandexCartDiscountId),
                        std::to_string(impl::kGiftProductForCartTypeId),
                        kYandexCartDiscountName, kYandexCartDiscountDescription,
                        kYandexCartDiscountPictureUri, impl::kOwn}}},
        "cofinancing_product_cart_discount",
    }};

template <class Promo>
void CheckPromoTypeInfo(const Promo& promo, const Promo& exp_promo) {
  EXPECT_EQ(promo.id, exp_promo.id);
  EXPECT_EQ(promo.type_id, exp_promo.type_id);
  EXPECT_EQ(promo.name, exp_promo.name);
  EXPECT_EQ(promo.description, exp_promo.description);
  EXPECT_EQ(promo.provider, exp_promo.provider);
  EXPECT_EQ(promo.picture_uri, exp_promo.picture_uri);
}

}  // namespace

TEST_P(TestCartDiscountsApplier, BasicTest) {
  const auto params = GetParam();
  applicators::CartDiscountsApplier cart_applier(params.discounts_response);
  auto discounts = cart_applier.Apply(params.cart_subtotal);

  // check new items
  EXPECT_EQ(discounts.new_items.size(), params.exp_new_items.size());

  for (size_t i = 0; i < discounts.new_items.size(); ++i) {
    const auto& cur_new_item = discounts.new_items[i];
    const auto& exp_new_item = params.exp_new_items[i];
    EXPECT_EQ(cur_new_item.item_id, exp_new_item.item_id);
    EXPECT_EQ(cur_new_item.quantity, exp_new_item.quantity);
    CheckPromoTypeInfo(cur_new_item.promo, exp_new_item.promo);
  }

  // check cart discounts
  EXPECT_EQ(discounts.cart_discounts.size(), params.exp_cart_discounts.size());
  for (size_t i = 0; i < discounts.cart_discounts.size(); ++i) {
    const auto& cur_cart_discount = discounts.cart_discounts[i];
    const auto& exp_cart_discount = params.exp_cart_discounts[i];
    EXPECT_EQ(cur_cart_discount.amount, exp_cart_discount.amount);
    CheckPromoTypeInfo(cur_cart_discount, exp_cart_discount);
  }
}

INSTANTIATE_TEST_SUITE_P(/* no prefix */, TestCartDiscountsApplier,
                         testing::ValuesIn(kBasicTestParams),
                         testing::PrintToStringParamName());

}  // namespace eats_discounts_applicator::tests
