#include <models/discounts/discount.hpp>

#include <gtest/gtest.h>

namespace {

namespace Discount = eats_products::models::discount;

template <typename T, typename U>
void AssertPercentage(T price, U promo_price, const std::string& expected) {
  const auto result = Discount::MakePercentageDiscount(price, promo_price);
  EXPECT_STREQ(result.data(), expected.data());
}

}  // namespace

TEST(Discount, MakePercentageSimple) { AssertPercentage(100, 10, "–90%"); }

TEST(Discount, MakePercentagePromoEqPrice) {
  AssertPercentage(100, 100, "–1%");
}

TEST(Discount, MakePercentagePromoEqPriceDouble) {
  AssertPercentage(100.12, 100.12, "–1%");
}

TEST(Discount, MakePercentagePromoZeroPrice) { AssertPercentage(0, 50, "–1%"); }

TEST(Discount, MakePercentagePromoZeroPriceDouble) {
  AssertPercentage(0.00, 50, "–1%");
}

TEST(Discount, MakePercentagePromoZeroPriceDouble2) {
  AssertPercentage(300.00, 299.00, "–1%");
}
