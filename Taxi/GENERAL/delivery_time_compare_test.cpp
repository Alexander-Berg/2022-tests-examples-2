#include <gtest/gtest.h>

#include "delivery_time_compare.hpp"

using eats_catalog::models::DeliveryTimeCompareValue;
using eats_catalog::models::InfinityDeliveryTime;

TEST(DeliveryTimeCompareValue, ThirtyLessSixty) {
  DeliveryTimeCompareValue thirty(std::chrono::minutes(30));
  DeliveryTimeCompareValue sixty(std::chrono::minutes(60));
  ASSERT_LT(thirty, sixty);
}

TEST(DeliveryTimeCompareValue, ThirtyLessInf) {
  DeliveryTimeCompareValue thirty(std::chrono::minutes(30));
  DeliveryTimeCompareValue inf{InfinityDeliveryTime()};
  ASSERT_LT(thirty, inf);
}

TEST(DeliveryTimeCompareValue, InfLessThirty) {
  DeliveryTimeCompareValue thirty(std::chrono::minutes(30));
  DeliveryTimeCompareValue inf{InfinityDeliveryTime()};
  ASSERT_FALSE(inf < thirty);
}

TEST(DeliveryTimeCompareValue, InfLessInf) {
  DeliveryTimeCompareValue lhs{InfinityDeliveryTime()};
  DeliveryTimeCompareValue rhs{InfinityDeliveryTime()};
  ASSERT_FALSE(lhs < rhs);
}
