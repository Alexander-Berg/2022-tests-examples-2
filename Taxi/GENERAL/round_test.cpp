#include <gtest/gtest.h>

#include <utils/round.hpp>

// EXPECT_EQ is used here on purpose (instead of EXPECT_DOUBLE_EQ)

TEST(Round, Round) {
  using utils::Round;

  EXPECT_EQ(Round(2.3), 2.0);
  EXPECT_EQ(Round(-2.3), -2.0);
  EXPECT_EQ(Round(6.7), 7.0);
  EXPECT_EQ(Round(-6.7), -7.0);

  constexpr double kPi = 3.141592653589793238;

  EXPECT_EQ(Round(kPi), 3);
  EXPECT_EQ(Round(kPi, 0), 3);
  EXPECT_EQ(Round(kPi, 1), 3.1);
  EXPECT_EQ(Round(kPi, 2), 3.14);
  EXPECT_EQ(Round(kPi, 3), 3.142);
  EXPECT_EQ(Round(kPi, 4), 3.1416);
  EXPECT_EQ(Round(kPi, 5), 3.14159);
  EXPECT_EQ(Round(kPi, 6), 3.141593);
  EXPECT_EQ(Round(kPi, 7), 3.1415927);
  EXPECT_EQ(Round(kPi, 8), 3.14159265);
  EXPECT_EQ(Round(kPi, 9), 3.141592654);
  EXPECT_EQ(Round(kPi, 10), 3.1415926536);

  EXPECT_EQ(Round(-kPi), -3);
  EXPECT_EQ(Round(-kPi, 0), -3);
  EXPECT_EQ(Round(-kPi, 1), -3.1);
  EXPECT_EQ(Round(-kPi, 2), -3.14);
  EXPECT_EQ(Round(-kPi, 3), -3.142);
  EXPECT_EQ(Round(-kPi, 4), -3.1416);
  EXPECT_EQ(Round(-kPi, 5), -3.14159);
  EXPECT_EQ(Round(-kPi, 6), -3.141593);
  EXPECT_EQ(Round(-kPi, 7), -3.1415927);
  EXPECT_EQ(Round(-kPi, 8), -3.14159265);
  EXPECT_EQ(Round(-kPi, 9), -3.141592654);
  EXPECT_EQ(Round(-kPi, 10), -3.1415926536);

  EXPECT_EQ(Round(1.99999999999, 5), 2.0);
  EXPECT_EQ(Round(-1.99999999999, 5), -2.0);
}

TEST(Round, RoundPrice) {
  using utils::RoundPrice;

  EXPECT_EQ(RoundPrice(2152.23456, 1.0), 2153);
  EXPECT_EQ(RoundPrice(2152.23456, 10.0), 2160);
  EXPECT_EQ(RoundPrice(2152.23456, 100.0), 2200);
  EXPECT_EQ(RoundPrice(2152.23456, 0.1), 2152.3);
  EXPECT_EQ(RoundPrice(2152.23456, 0.01), 2152.24);
  EXPECT_EQ(RoundPrice(2152.23456, 0.001), 2152.235);

  EXPECT_EQ(RoundPrice(38.39, 0.1), 38.4);
  EXPECT_EQ(RoundPrice(38.4, 0.1), 38.4);

  // this magic number may appear when calculating 149 * (49 / 149)
  EXPECT_EQ(RoundPrice(49.00000000000001, 1.0), 49.0);
  EXPECT_EQ(RoundPrice(49.00000000000001, 0.01), 49.0);

  // this magic number may appear when calculating 156 * (95 / 156)
  EXPECT_EQ(RoundPrice(94.99999999999999, 1.0), 95.0);
  EXPECT_EQ(RoundPrice(94.99999999999999, 0.01), 95.0);

  // testing how inside kDoubleInaccuracyNDigits works
  EXPECT_EQ(RoundPrice(49.00000001, 1.0), 50.0);
  EXPECT_EQ(RoundPrice(49.000000001, 1.0), 49.0);
}
