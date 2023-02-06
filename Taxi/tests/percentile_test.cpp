#include <userver/utest/utest.hpp>

#include <stdexcept>
#include <utility>

#include <common/percentile.hpp>

void CheckOneValuePercentile(int value, int expected) {
  auto percentile = stq_agent::common::Percentile{};
  percentile.Account(value);
  EXPECT_EQ(percentile.GetPercentile(100), expected);
}

TEST(percentile, basic) { CheckOneValuePercentile(3, 3); }

TEST(percentile, invalid_percent) {
  auto percentile = stq_agent::common::Percentile{};
  percentile.Account(3);
  EXPECT_THROW(percentile.GetPercentile(-1), std::invalid_argument);
  EXPECT_THROW(percentile.GetPercentile(101), std::invalid_argument);
}

TEST(percentile, no_accounts) {
  auto percentile = stq_agent::common::Percentile{};
  EXPECT_EQ(percentile.GetPercentile(100), 0);
  EXPECT_EQ(percentile.GetPercentile(50), 0);
  EXPECT_EQ(percentile.GetPercentile(1), 0);
  EXPECT_EQ(percentile.GetPercentile(0), 0);
}

TEST(percentile, scaling) {
  CheckOneValuePercentile(60, 61);
  CheckOneValuePercentile(61, 61);
  CheckOneValuePercentile(62, 63);
  CheckOneValuePercentile(63, 63);

  CheckOneValuePercentile(100, 102);
  CheckOneValuePercentile(101, 102);
  CheckOneValuePercentile(102, 102);
  CheckOneValuePercentile(103, 102);
  CheckOneValuePercentile(104, 102);

  CheckOneValuePercentile(105, 107);
  CheckOneValuePercentile(106, 107);
  CheckOneValuePercentile(107, 107);
  CheckOneValuePercentile(108, 107);
  CheckOneValuePercentile(109, 107);

  CheckOneValuePercentile(345678, 343900);
  CheckOneValuePercentile(348899, 343900);
  CheckOneValuePercentile(348900, 353900);
}

TEST(percentile, min_max) {
  CheckOneValuePercentile(-1, 0);
  CheckOneValuePercentile(-10000000, 0);
  CheckOneValuePercentile(388900, 383900);
  CheckOneValuePercentile(500000, 383900);
  CheckOneValuePercentile(1000000, 383900);
  CheckOneValuePercentile(10000000, 383900);
}

TEST(percentile, calc_percentile_1) {
  auto percentile = stq_agent::common::Percentile{};

  percentile.Account(10);
  EXPECT_EQ(percentile.GetPercentile(100), 10);
  EXPECT_EQ(percentile.GetPercentile(98), 10);
  EXPECT_EQ(percentile.GetPercentile(50), 10);
  EXPECT_EQ(percentile.GetPercentile(1), 10);

  percentile.Account(20);
  EXPECT_EQ(percentile.GetPercentile(100), 20);
  EXPECT_EQ(percentile.GetPercentile(51), 20);
  EXPECT_EQ(percentile.GetPercentile(50), 10);
  EXPECT_EQ(percentile.GetPercentile(1), 10);
}

TEST(percentile, calc_percentile_2) {
  auto percentile = stq_agent::common::Percentile{};

  for (auto i = 1; i <= 100; ++i) {
    percentile.Account(i);
  }

  EXPECT_EQ(percentile.GetPercentile(100), 102);
  EXPECT_EQ(percentile.GetPercentile(99), 99);
  EXPECT_EQ(percentile.GetPercentile(98), 99);
  EXPECT_EQ(percentile.GetPercentile(97), 97);
  EXPECT_EQ(percentile.GetPercentile(96), 97);
  EXPECT_EQ(percentile.GetPercentile(95), 95);
  EXPECT_EQ(percentile.GetPercentile(50), 51);
  EXPECT_EQ(percentile.GetPercentile(49), 49);
  EXPECT_EQ(percentile.GetPercentile(48), 48);
  EXPECT_EQ(percentile.GetPercentile(47), 47);
  EXPECT_EQ(percentile.GetPercentile(3), 3);
  EXPECT_EQ(percentile.GetPercentile(2), 2);
  EXPECT_EQ(percentile.GetPercentile(1), 1);
}

TEST(percentile, calc_percentile_3) {
  auto percentile = stq_agent::common::Percentile{};

  percentile.Account(1899);
  percentile.Account(1900);

  EXPECT_EQ(percentile.GetPercentile(100), 1950);
  EXPECT_EQ(percentile.GetPercentile(51), 1950);
  EXPECT_EQ(percentile.GetPercentile(50), 1875);
  EXPECT_EQ(percentile.GetPercentile(1), 1875);
}

TEST(percentile, zero) {
  auto percentile = stq_agent::common::Percentile{};

  percentile.Account(0);
  EXPECT_EQ(percentile.GetPercentile(100), 0);
  EXPECT_EQ(percentile.GetPercentile(75), 0);
  EXPECT_EQ(percentile.GetPercentile(50), 0);
  EXPECT_EQ(percentile.GetPercentile(1), 0);

  percentile.Account(0);
  percentile.Account(0);
  percentile.Account(10);
  EXPECT_EQ(percentile.GetPercentile(100), 10);
  EXPECT_EQ(percentile.GetPercentile(76), 10);
  EXPECT_EQ(percentile.GetPercentile(75), 0);
  EXPECT_EQ(percentile.GetPercentile(50), 0);
  EXPECT_EQ(percentile.GetPercentile(1), 0);
}

TEST(percentile, zero_percent_1) {
  auto percentile = stq_agent::common::Percentile{};
  percentile.Account(49);
  EXPECT_EQ(percentile.GetPercentile(0), 49);
  percentile.Account(50);
  EXPECT_EQ(percentile.GetPercentile(0), 49);
  percentile.Account(100);
  EXPECT_EQ(percentile.GetPercentile(0), 49);
  percentile.Account(1);
  EXPECT_EQ(percentile.GetPercentile(0), 1);
  percentile.Account(0);
  EXPECT_EQ(percentile.GetPercentile(0), 0);
  percentile.Account(-1);
  EXPECT_EQ(percentile.GetPercentile(0), 0);
  percentile.Account(-10);
  EXPECT_EQ(percentile.GetPercentile(0), 0);
}

TEST(percentile, zero_percent_2) {
  auto percentile = stq_agent::common::Percentile{};
  percentile.Account(10000000);
  EXPECT_EQ(percentile.GetPercentile(0), 383900);
  percentile.Account(10000000);
  EXPECT_EQ(percentile.GetPercentile(0), 383900);
  percentile.Account(348899);
  EXPECT_EQ(percentile.GetPercentile(0), 343900);
}

TEST(percentile, empty_percentile_iterators) {
  const auto percentile = stq_agent::common::Percentile{};
  ASSERT_EQ(percentile.begin(), percentile.end());
}

TEST(percentile, iterators) {
  auto percentile = stq_agent::common::Percentile{};
  percentile.Account(10, 1);
  percentile.Account(62, 2);
  percentile.Account(109, 3);

  auto it = percentile.begin();

  ASSERT_EQ(it, percentile.begin());
  ASSERT_NE(it, percentile.end());
  ASSERT_EQ(*it, std::make_pair(10, 1));
  ++it;
  ASSERT_NE(it, percentile.begin());
  ASSERT_NE(it, percentile.end());
  ASSERT_EQ(*it, std::make_pair(63, 2));
  ++it;
  ASSERT_NE(it, percentile.begin());
  ASSERT_NE(it, percentile.end());
  ASSERT_EQ(*it, std::make_pair(107, 3));
  ++it;
  ASSERT_NE(it, percentile.begin());
  ASSERT_EQ(it, percentile.end());
}
