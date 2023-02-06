#include <gtest/gtest.h>

#include <taxi_config/variables/EATS_PLUS_ROUNDING_AND_PRECISION_BY_CURRENCY_V2.hpp>

#include "decimal_utils.hpp"

TEST(DecimalUtils, RoundingPrecisionLoss17299999999999997) {
  double cashback_before_rounding = 7.6 + 9.7;
  auto result = eats_plus::utils::RoundCashback(
      cashback_before_rounding, 1,
      taxi_config::eats_plus_rounding_and_precision_by_currency_v2::
          RoundPolicy::kNullRoundPolicy);
  ASSERT_EQ("17.3", ToString(result));
}
