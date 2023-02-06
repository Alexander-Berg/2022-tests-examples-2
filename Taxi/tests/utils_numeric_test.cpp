#include <userver/utest/utest.hpp>
#include "utils/numeric.hpp"

namespace eats_restapp_marketing::utils::numeric {

TEST(RoundByPoint, RoundNull) {
  double value = 0.0032;
  ASSERT_EQ(RoundByPoint(value), 0);
}

TEST(RoundByPoint, RoundOne) {
  double value = 0.0075;
  ASSERT_EQ(RoundByPoint(value), 0.01);
}

TEST(RoundByPoint, RoundThreePoint) {
  double value = 0.0032;
  ASSERT_EQ(RoundByPoint(value, 3), 0.003);
}

TEST(RoundByPoint, RoundThreePointTwo) {
  double value = 0.0075;
  ASSERT_EQ(RoundByPoint(value, 3), 0.008);
}

}  // namespace eats_restapp_marketing::utils::numeric
