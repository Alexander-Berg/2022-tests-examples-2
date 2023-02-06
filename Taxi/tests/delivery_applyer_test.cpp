#include <optional>

#include <gtest/gtest.h>

#include <applicators/cart.hpp>
#include <eats-discounts-applicator/delivery_applyer.hpp>
#include <experiments3.hpp>
#include <tests/utils.hpp>

namespace eats_discounts_applicator::tests {

namespace {
void CheckDeliveryDiscount(const std::optional<Money>& exp_place_amount,
                           const std::optional<Money>& exp_yandex_amount,
                           const DeliveryDiscount& delivery_discount) {
  if (exp_place_amount.has_value()) {
    EXPECT_NE(delivery_discount.place_discount, std::nullopt);
    EXPECT_EQ(delivery_discount.place_discount.value().id, kPlaceDeliveryId);
    EXPECT_EQ(delivery_discount.place_discount.value().name,
              kPlaceDeliveryName);
    EXPECT_EQ(delivery_discount.place_discount.value().description,
              kPlaceDeliveryDescription);
    EXPECT_EQ(delivery_discount.place_discount.value().picture_uri,
              kPlaceDeliveryPictureUri);
    EXPECT_EQ(delivery_discount.place_discount.value().amount,
              exp_place_amount.value());
  } else {
    EXPECT_EQ(delivery_discount.place_discount, std::nullopt);
  }

  if (exp_yandex_amount.has_value()) {
    EXPECT_NE(delivery_discount.yandex_discount, std::nullopt);
    EXPECT_EQ(delivery_discount.yandex_discount.value().id, kYandexDeliveryId);
    EXPECT_EQ(delivery_discount.yandex_discount.value().name,
              kYandexDeliveryName);
    EXPECT_EQ(delivery_discount.yandex_discount.value().description,
              kYandexDeliveryDescription);
    EXPECT_EQ(delivery_discount.yandex_discount.value().picture_uri,
              kYandexDeliveryPictureUri);
    EXPECT_EQ(delivery_discount.yandex_discount.value().amount,
              exp_yandex_amount.value());
  } else {
    EXPECT_EQ(delivery_discount.yandex_discount, std::nullopt);
  }
}
}  // namespace

namespace not_table_discounts {

namespace {

Money kDeliveryFee{102};

struct TestParams {
  requesters::MatchedDiscounts discounts_response;
  std::optional<Money> exp_place_amount;
  std::optional<Money> exp_yandex_amount;
  std::string test_name;
};

class TestDeliveryApplyer : public testing::TestWithParam<TestParams> {};

std::string PrintToString(const TestParams& params) { return params.test_name; }

const std::vector<TestParams> kBasicTestParams = {
    {
        requesters::ParseMatchResponse(
            {MakeDeliveryDiscountResponse(
                DeliveryDiscountType::NoDiscount /*place_discount_type*/,
                DeliveryDiscountType::NoDiscount /*yandex_discount_type*/)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        std::nullopt,
        std::nullopt,
        "no_discounts",
    },
    {
        requesters::ParseMatchResponse(
            {MakeDeliveryDiscountResponse(
                DeliveryDiscountType::AbsoluteValue /*place_discount_type*/,
                DeliveryDiscountType::NoDiscount /*yandex_discount_type*/,
                "10" /*value*/)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        Money(10),
        std::nullopt,
        "place_discount",
    },
    {
        requesters::ParseMatchResponse(
            {MakeDeliveryDiscountResponse(
                DeliveryDiscountType::AbsoluteValue /*place_discount_type*/,
                DeliveryDiscountType::NoDiscount /*yandex_discount_type*/,
                "300" /*value*/)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        kDeliveryFee,
        std::nullopt,
        "big_place_discount",
    },
    {
        requesters::ParseMatchResponse(
            {MakeDeliveryDiscountResponse(
                DeliveryDiscountType::NoDiscount /*place_discount_type*/,
                DeliveryDiscountType::AbsoluteValue /*yandex_discount_type*/,
                "10" /*value*/)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        std::nullopt,
        Money(10),
        "yandex_discount",
    },
    {
        requesters::ParseMatchResponse(
            {MakeDeliveryDiscountResponse(
                DeliveryDiscountType::NoDiscount /*place_discount_type*/,
                DeliveryDiscountType::AbsoluteValue /*yandex_discount_type*/,
                "300" /*value*/)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        std::nullopt,
        kDeliveryFee,
        "big_yandex_discount",
    },
    {
        requesters::ParseMatchResponse(
            {MakeDeliveryDiscountResponse(
                DeliveryDiscountType::AbsoluteValue /*place_discount_type*/,
                DeliveryDiscountType::AbsoluteValue /*yandex_discount_type*/,
                "10" /*value*/)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        Money(10),
        Money(10),
        "place_yandex_discount",
    },
    {
        requesters::ParseMatchResponse(
            {MakeDeliveryDiscountResponse(
                DeliveryDiscountType::AbsoluteValue /*place_discount_type*/,
                DeliveryDiscountType::AbsoluteValue /*yandex_discount_type*/,
                "10" /*value*/, std::nullopt /*max_discount*/,
                "koko" /*promotype*/)},
            experiments::ExcludedInformation{{"koko", "two"},
                                             kEmptyExcludedDiscounts},
            {{"koko", {"name", "descr", "pict"}}}),
        std::nullopt,
        std::nullopt,
        "exclude_discount_for_delivery_with_promo",
    },
    {
        requesters::ParseMatchResponse(
            {MakeDeliveryDiscountResponse(
                DeliveryDiscountType::AbsoluteValue /*place_discount_type*/,
                DeliveryDiscountType::AbsoluteValue /*yandex_discount_type*/,
                "300" /*value*/)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        kDeliveryFee,
        std::nullopt,
        "big_place_big_yandex_discount",
    },
    {
        requesters::ParseMatchResponse(
            {MakeDeliveryDiscountResponse(
                DeliveryDiscountType::
                    FractionWithMaximum /*place_discount_type*/,
                DeliveryDiscountType::
                    FractionWithMaximum /*yandex_discount_type*/,
                "50" /*value*/)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        Money(51),
        Money(51),
        "place_yandex_percent_discount",
    },
    {
        requesters::ParseMatchResponse(
            {MakeDeliveryDiscountResponse(
                DeliveryDiscountType::
                    FractionWithMaximum /*place_discount_type*/,
                DeliveryDiscountType::
                    FractionWithMaximum /*yandex_discount_type*/,
                "60" /*value*/)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        Money("61.2"),
        Money("40.8"),
        "place_yandex_percent_2_discount",
    },
    {
        requesters::ParseMatchResponse(
            {MakeDeliveryDiscountResponse(
                DeliveryDiscountType::
                    FractionWithMaximum /*place_discount_type*/,
                DeliveryDiscountType::
                    FractionWithMaximum /*yandex_discount_type*/,
                "60" /*value*/, "33.33" /*max_discount*/)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        Money("33.33"),
        Money("33.33"),
        "place_yandex_percent_3_discount",
    },
    {
        requesters::ParseMatchResponse(
            {MakeDeliveryDiscountResponse(
                DeliveryDiscountType::AbsoluteValue /*place_discount_type*/,
                DeliveryDiscountType::NoDiscount /*yandex_discount_type*/,
                "10" /*value*/)},
            experiments::ExcludedInformation{
                {}, {ExpDiscountType::kPlaceDeliveryDiscount}},
            kPromoTypesInfo),
        std::nullopt,
        std::nullopt,
        "place_discount_disable_by_exp",
    },
    {
        requesters::ParseMatchResponse(
            {MakeDeliveryDiscountResponse(
                DeliveryDiscountType::NoDiscount /*place_discount_type*/,
                DeliveryDiscountType::AbsoluteValue /*yandex_discount_type*/,
                "10" /*value*/)},
            experiments::ExcludedInformation{
                {}, {ExpDiscountType::kYandexDeliveryDiscount}},
            kPromoTypesInfo),
        std::nullopt,
        std::nullopt,
        "yandex_discount_disable_by_exp",
    },
};

template <class Item>
void CheckItem(const Item& item, const Item& exp_item) {
  EXPECT_EQ(item.public_id, exp_item.public_id);
  EXPECT_EQ(item.price, exp_item.price);
  EXPECT_EQ(item.quantity, exp_item.quantity);
}

}  // namespace

TEST_P(TestDeliveryApplyer, BasicTest) {
  const auto params = GetParam();
  CartForDiscount cart{
      {{1, "1", Money(100), std::nullopt, 1, {}, std::nullopt}}, Money{0}};
  auto cart_result =
      applicators::ApplyDiscountsForCart(cart, {}, params.discounts_response);

  // cart_subtotal doesn't matter with not table discounts(old flow)
  auto delivery_discount = cart_result.delivery_applyer.Apply(
      kDeliveryFee, kZeroMoney /*cart_subtotal*/);

  CheckDeliveryDiscount(params.exp_place_amount, params.exp_yandex_amount,
                        delivery_discount);
}

INSTANTIATE_TEST_SUITE_P(/* no prefix */, TestDeliveryApplyer,
                         testing::ValuesIn(kBasicTestParams),
                         testing::PrintToStringParamName());

}  // namespace not_table_discounts

namespace table_discounts {

namespace {

struct TestParams {
  requesters::MatchedDiscounts discounts_response;
  Money delivery_fee;
  Money cart_subtotal;
  std::optional<Money> exp_place_amount;
  std::optional<Money> exp_yandex_amount;
  std::string test_name;
};

class TestDeliveryApplyerTableValue
    : public testing::TestWithParam<TestParams> {};

class TestDeliveryApplyerTableValueRoundDiscount
    : public testing::TestWithParam<TestParams> {};

std::string PrintToString(const TestParams& params) { return params.test_name; }

const std::vector<TableData> kTableData = {
    TableData{DiscountType::AbsoluteValue /*type*/, "100" /*from cost*/,
              "15" /*value*/},
    TableData{DiscountType::FractionWithMaximum /*type*/, "500" /*from cost*/,
              "10" /*value*/}};

const std::vector<TestParams> kBasicTestParams = {
    {
        requesters::ParseMatchResponse(
            {MakeTableDeliveryDiscountResponse(kTableData)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        Money(100) /*delivery_fee*/,
        Money(80) /*cart_subtotal*/,
        std::nullopt /*exp_place_amount*/,
        std::nullopt /*exp_yandex_amount*/,
        "no_discounts",
    },
    {
        requesters::ParseMatchResponse(
            {MakeTableDeliveryDiscountResponse(kTableData)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        Money(100) /*delivery_fee*/,
        Money(100) /*cart_subtotal*/,
        Money(15) /*exp_place_amount*/,
        Money(15) /*exp_yandex_amount*/,
        "first_table_discount",
    },
    {
        requesters::ParseMatchResponse(
            {MakeTableDeliveryDiscountResponse(kTableData)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        Money(10) /*delivery_fee*/,
        Money(100) /*cart_subtotal*/,
        Money(10) /*exp_place_amount*/,
        std::nullopt /*exp_yandex_amount*/,
        "big_first_table_discount",
    },
    {
        requesters::ParseMatchResponse(
            {MakeTableDeliveryDiscountResponse(kTableData)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        Money(10) /*delivery_fee*/,
        Money(500) /*cart_subtotal*/,
        Money(1) /*exp_place_amount*/,
        Money(1) /*exp_yandex_amount*/,
        "second_table_discount",
    },
    {
        requesters::ParseMatchResponse(
            {MakeTableDeliveryDiscountResponse(kTableData)},
            experiments::ExcludedInformation{
                {}, {ExpDiscountType::kPlaceDeliveryDiscount}},
            kPromoTypesInfo),
        Money(100) /*delivery_fee*/,
        Money(100) /*cart_subtotal*/,
        std::nullopt /*exp_place_amount*/,
        Money(15) /*exp_yandex_amount*/,
        "place_discount_disable_by_exp",
    },
    {
        requesters::ParseMatchResponse(
            {MakeTableDeliveryDiscountResponse(kTableData)},
            experiments::ExcludedInformation{
                {}, {ExpDiscountType::kYandexDeliveryDiscount}},
            kPromoTypesInfo),
        Money(100) /*delivery_fee*/,
        Money(100) /*cart_subtotal*/,
        Money(15) /*exp_place_amount*/,
        std::nullopt /*exp_yandex_amount*/,
        "yandex_discount_disable_by_exp",
    }};

const std::vector<TableData> kRoundTableData = {
    TableData{DiscountType::AbsoluteValue /*type*/, "100" /*from cost*/,
              "15.20" /*value*/},
    TableData{DiscountType::FractionWithMaximum /*type*/, "500" /*from cost*/,
              "10" /*value*/}};

const std::vector<TestParams> kRoundTestParams = {
    {
        requesters::ParseMatchResponse(
            {MakeTableDeliveryDiscountResponse(kRoundTableData)},
            experiments::ExcludedInformation{
                {}, {ExpDiscountType::kPlaceDeliveryDiscount}},
            kPromoTypesInfo),
        Money(100) /*delivery_fee*/,
        Money(100) /*cart_subtotal*/,
        std::nullopt /*exp_place_amount*/,
        Money(16) /*exp_yandex_amount*/,
        "yandex_pays_round",
    },
    {
        requesters::ParseMatchResponse(
            {MakeTableDeliveryDiscountResponse(kRoundTableData)},
            experiments::ExcludedInformation{
                {}, {ExpDiscountType::kYandexDeliveryDiscount}},
            kPromoTypesInfo),
        Money(100) /*delivery_fee*/,
        Money(100) /*cart_subtotal*/,
        Money(16) /*exp_place_amount*/,
        std::nullopt /*exp_yandex_amount*/,
        "place_pays_round",
    },
    {
        requesters::ParseMatchResponse(
            {MakeTableDeliveryDiscountResponse(kRoundTableData)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        Money(100) /*delivery_fee*/,
        Money(100) /*cart_subtotal*/,
        Money("15.20") /*exp_place_amount*/,
        Money("15.80") /*exp_yandex_amount*/,
        "both_but_yandex_pays_round",
    },
    {
        requesters::ParseMatchResponse(
            {MakeTableDeliveryDiscountResponse(kTableData)},
            kEmptyExcludedInformation, kPromoTypesInfo),
        Money(100) /*delivery_fee*/,
        Money(100) /*cart_subtotal*/,
        Money(15) /*exp_place_amount*/,
        Money(15) /*exp_yandex_amount*/,
        "both_no_one_pays_round",
    }};

template <class Item>
void CheckItem(const Item& item, const Item& exp_item) {
  EXPECT_EQ(item.public_id, exp_item.public_id);
  EXPECT_EQ(item.price, exp_item.price);
  EXPECT_EQ(item.quantity, exp_item.quantity);
}

}  // namespace

TEST_P(TestDeliveryApplyerTableValue, BasicTest) {
  const auto params = GetParam();
  CartForDiscount cart{
      {{1, "1", Money(100), std::nullopt, 1, {}, std::nullopt}}, Money{0}};
  auto cart_result =
      applicators::ApplyDiscountsForCart(cart, {}, params.discounts_response);

  auto delivery_discount = cart_result.delivery_applyer.Apply(
      params.delivery_fee, params.cart_subtotal /*cart_subtotal*/);

  CheckDeliveryDiscount(params.exp_place_amount, params.exp_yandex_amount,
                        delivery_discount);
}

TEST_P(TestDeliveryApplyerTableValueRoundDiscount, RoundTest) {
  const auto params = GetParam();
  CartForDiscount cart{
      {{1, "1", Money(100), std::nullopt, 1, {}, std::nullopt}}, Money{0}};
  ApplyDiscountsForCartSettings settings{Money(1)};
  auto cart_result = applicators::ApplyDiscountsForCart(
      cart, settings, params.discounts_response);

  auto delivery_discount = cart_result.delivery_applyer.Apply(
      params.delivery_fee, params.cart_subtotal /*cart_subtotal*/);

  CheckDeliveryDiscount(params.exp_place_amount, params.exp_yandex_amount,
                        delivery_discount);
}

INSTANTIATE_TEST_SUITE_P(/* no prefix */, TestDeliveryApplyerTableValue,
                         testing::ValuesIn(kBasicTestParams),
                         testing::PrintToStringParamName());

INSTANTIATE_TEST_SUITE_P(/* no prefix */,
                         TestDeliveryApplyerTableValueRoundDiscount,
                         testing::ValuesIn(kRoundTestParams),
                         testing::PrintToStringParamName());

}  // namespace table_discounts

}  // namespace eats_discounts_applicator::tests
