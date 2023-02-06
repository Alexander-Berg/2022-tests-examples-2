#include <gtest/gtest.h>

#include "apply_promocode_discount.hpp"

TEST(ApplyPromocodeDiscount, ZeroDiscount) {
  auto result = eats_plus::utils::ApplyPromocodeDiscount(
      ::grocery_pricing::Numeric(100), 0.0);
  ASSERT_TRUE(result == grocery_pricing::Numeric(0));
}

TEST(ApplyPromocodeDiscount, HappyPath) {
  auto result = eats_plus::utils::ApplyPromocodeDiscount(
      ::grocery_pricing::Numeric(100), 0.8);
  ASSERT_TRUE(result == grocery_pricing::Numeric(80));
}

TEST(ApplyPromocodeDiscount, RoundResult) {
  auto result = eats_plus::utils::ApplyPromocodeDiscount(
      ::grocery_pricing::Numeric(100), 0.7999999);
  ASSERT_EQ(result, ::grocery_pricing::Numeric(80));
}

TEST(ApplyPromocodeDiscount, NotRoundResult) {
  auto result = eats_plus::utils::ApplyPromocodeDiscount(
      ::grocery_pricing::Numeric(100), 0.79);
  ASSERT_EQ(result, ::grocery_pricing::Numeric(79));
}
