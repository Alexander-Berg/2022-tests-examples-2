#include <gtest/gtest.h>

#include <utils/cost_usage.hpp>

namespace coupons {
TEST(CheckCostUsage, CheckSmallValuePromocode) {
  double order_cost = 100;
  double value = 20;
  EXPECT_EQ(CalculateCostUsage(value, std::nullopt, std::nullopt, order_cost),
            value);
}

TEST(CheckCostUsage, CheckBigValuePromocode) {
  double order_cost = 100;
  double value = 200;
  EXPECT_EQ(CalculateCostUsage(value, std::nullopt, std::nullopt, order_cost),
            order_cost);
}

TEST(CheckCostUsage, CheckPercentPromocode) {
  double order_cost = 100;
  double value = 20;
  double percent = 80;
  // yes, percent ignoers value
  // expect just percent because order_cost = 100
  EXPECT_EQ(CalculateCostUsage(value, percent, std::nullopt, order_cost),
            percent);
}

TEST(CheckCostUsage, CheckPercentSmallLimitPromocode) {
  double order_cost = 100;
  double value = 20;
  double percent = 80;
  double limit = 60;
  // yes, percent ignoers value
  EXPECT_EQ(CalculateCostUsage(value, percent, limit, order_cost), limit);
}

TEST(CheckCostUsage, CheckPercentBigLimitPromocode) {
  double order_cost = 100;
  double value = 20;
  double percent = 80;
  double limit = 90;
  // yes, percent ignoers value
  EXPECT_EQ(CalculateCostUsage(value, percent, limit, order_cost), percent);
}

}  // namespace coupons
