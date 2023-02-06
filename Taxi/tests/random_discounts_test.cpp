#include <userver/utest/utest.hpp>

#include <experiments3/random_discounts.hpp>
#include <views/4.0/random-discounts/random_roller.hpp>

namespace roller {
using DiscountSettings = experiments3::random_discounts::ValueDiscountsettingsA;

TEST(CheckRandomDiscountsRoll, CheckRollDice) {
  RandomRoller roller{{{"failure", 1, 1, 0},
                       {"1_first_s", 1, 1, 0.01},
                       {"10_second_s", 1, 1, 10},
                       {"failure", 1, 1, 0},
                       {"20_third_s", 1, 1, 20},
                       {"failure", 1, 1, 0}}};
  int dice_max = 10000;
  {
    const auto& result = roller.ProcessRollInternal(1);
    EXPECT_TRUE(result);
    EXPECT_EQ(result->discount_series, "1_first_s");
  }
  {
    const auto& result = roller.ProcessRollInternal(2);
    EXPECT_TRUE(result);
    EXPECT_EQ(result->discount_series, "10_second_s");
  }
  {
    const auto& result = roller.ProcessRollInternal(555);
    EXPECT_TRUE(result);
    EXPECT_EQ(result->discount_series, "10_second_s");
  }
  {
    const auto& result = roller.ProcessRollInternal(1001);
    EXPECT_TRUE(result);
    EXPECT_EQ(result->discount_series, "10_second_s");
  }
  {
    const auto& result = roller.ProcessRollInternal(1002);
    EXPECT_TRUE(result);
    EXPECT_EQ(result->discount_series, "20_third_s");
  }
  {
    const auto& result = roller.ProcessRollInternal(2222);
    EXPECT_TRUE(result);
    EXPECT_EQ(result->discount_series, "20_third_s");
  }
  {
    const auto& result = roller.ProcessRollInternal(3001);
    EXPECT_TRUE(result);
    EXPECT_EQ(result->discount_series, "20_third_s");
  }
  {
    const auto& result = roller.ProcessRollInternal(3002);
    EXPECT_FALSE(result);
  }
  {
    const auto& result = roller.ProcessRollInternal(7777);
    EXPECT_FALSE(result);
  }
  {
    const auto& result = roller.ProcessRollInternal(dice_max);
    EXPECT_FALSE(result);
  }
  {
    const auto& result = roller.ProcessRollInternal(dice_max + 100);
    EXPECT_FALSE(result);
  }
  {
    const auto& result = roller.ProcessRollInternal(-5555);
    EXPECT_FALSE(result);
  }
}

TEST(CheckRandomDiscountsRoll, CheckSettings) {
  {
    RandomRoller roller{{}};
    auto result = roller.ProcessRollInternal(1);
    EXPECT_FALSE(result);
    result = roller.ProcessRollInternal(0);
    EXPECT_FALSE(result);
  }
  {
    RandomRoller roller{{{"failure", 1, 1, 0}}};
    const auto& result = roller.ProcessRollInternal(1);
    EXPECT_FALSE(result);
  }
  {
    EXPECT_THROW(RandomRoller roller({{"sss", 1, 1, 130}}), std::runtime_error);
  }
}
}  // namespace roller
