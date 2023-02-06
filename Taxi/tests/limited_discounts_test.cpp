#include <grocery-discounts-calculator/apply.hpp>
#include <grocery-discounts-calculator/calculation_log.hpp>
#include <grocery-discounts-calculator/pricing.hpp>

#include <grocery-discounts-calculator/limited_discounts.hpp>
#include "utils_test.hpp"

#include <userver/fs/blocking/read.hpp>
#include <userver/utest/utest.hpp>

#include <optional>

namespace grocery_discounts_calculator {

using ProductId = grocery_shared::ProductId;
using grocery_pricing::Numeric;

TEST(Limited_Discounts, happy_path) {
  const auto initial_pricing = Pricing{
      {ProductPricing(ProductId{"product-1"}, Numeric{354}, Numeric{1})},
      Numeric{1}};

  DiscountMeta meta_1;
  meta_1.discount_id = "123";
  meta_1.has_discount_usage_restrictions = true;
  const auto money_payment_absolute_1 = MakePaymentMethodDiscount(
      ProductId{"product-1"}, AbsoluteMoneyPayment{Numeric{30}},
      std::move(meta_1));

  DiscountMeta meta_2;
  meta_2.discount_id = "456";
  meta_2.has_discount_usage_restrictions = true;
  const auto money_payment_absolute_2 = MakePaymentMethodDiscount(
      ProductId{"product-1"}, AbsoluteMoneyPayment{Numeric{30}},
      std::move(meta_2));

  DiscountMeta meta_3;
  meta_3.discount_id = "789";
  meta_3.has_discount_usage_restrictions = false;
  const auto money_payment_absolute_3 = MakePaymentMethodDiscount(
      ProductId{"product-1"}, AbsoluteMoneyPayment{Numeric{30}},
      std::move(meta_3));

  const std::vector<Modifier> modifiers = {money_payment_absolute_1,
                                           money_payment_absolute_2};

  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});

  auto calc_log = MakeCalculationLog(resulting_pricing);
  const auto& limited_discounts = ExtractLimitedDiscounts(calc_log);
  std::vector<std::string> expected_response{"123", "456"};
  ASSERT_EQ(limited_discounts.value_or(std::vector<std::string>{}),
            expected_response);
}

TEST(Limited_Discounts, no_discount_id) {
  const auto initial_pricing = Pricing{
      {ProductPricing(ProductId{"product-1"}, Numeric{354}, Numeric{1})},
      Numeric{1}};

  DiscountMeta meta;
  meta.has_discount_usage_restrictions = true;
  const auto money_payment_absolute = MakePaymentMethodDiscount(
      ProductId{"product-1"}, AbsoluteMoneyPayment{Numeric{30}},
      std::move(meta));
  const std::vector<Modifier> modifiers = {money_payment_absolute};

  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});

  auto calc_log = MakeCalculationLog(resulting_pricing);
  const auto& limited_discounts = ExtractLimitedDiscounts(calc_log);
  ASSERT_EQ(limited_discounts, std::nullopt);
}

TEST(Limited_Discounts, no_restriction_specified) {
  const auto initial_pricing = Pricing{
      {ProductPricing(ProductId{"product-1"}, Numeric{354}, Numeric{1})},
      Numeric{1}};

  DiscountMeta meta;
  meta.discount_id = "123";
  const auto money_payment_absolute = MakePaymentMethodDiscount(
      ProductId{"product-1"}, AbsoluteMoneyPayment{Numeric{30}},
      std::move(meta));
  const std::vector<Modifier> modifiers = {money_payment_absolute};

  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});

  auto calc_log = MakeCalculationLog(resulting_pricing);
  const auto& limited_discounts = ExtractLimitedDiscounts(calc_log);
  ASSERT_EQ(limited_discounts, std::nullopt);
}

TEST(Limited_Discounts, cart_discount) {
  const auto initial_pricing = Pricing{
      {ProductPricing(ProductId{"product-1"}, Numeric{354}, Numeric{1})},
      Numeric{1}};

  DiscountMeta meta;
  meta.discount_id = "123";
  meta.has_discount_usage_restrictions = true;
  const auto cart_discount = MakeCartDiscount(
      {CartDiscountStep{Numeric{0}, AbsoluteCashbackGain{Numeric{50}}}},
      std::move(meta));
  const std::vector<Modifier> modifiers = {cart_discount};

  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});

  auto calc_log = MakeCalculationLog(resulting_pricing);
  const auto& limited_discounts = ExtractLimitedDiscounts(calc_log);
  std::vector<std::string> expected_response{"123"};

  ASSERT_EQ(limited_discounts, expected_response);
}

TEST(Limited_Discounts, wrong_json_structures) {
  auto calc_logs = ReadFile("wrong_json_structure_log.json");
  for (auto log : calc_logs["wrong_calc_logs"]) {
    const auto& limited_discounts = ExtractLimitedDiscounts(log);

    ASSERT_EQ(limited_discounts, std::nullopt);
  }
}

}  // namespace grocery_discounts_calculator
