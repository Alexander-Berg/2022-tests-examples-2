#include <gtest/gtest.h>

#include <userver/utils/datetime.hpp>

#include <utils/chrono.hpp>

TEST(DeviceNotifyChrono, DoubleSeconds) {
  std::chrono::milliseconds ms(100);
  utils::chrono::seconds_double d = ms;
  ASSERT_DOUBLE_EQ(d.count(), 0.1);

  const utils::chrono::seconds_double sec_zero = std::chrono::milliseconds(0);
  ASSERT_DOUBLE_EQ(sec_zero.count(), 0.0);

  const utils::chrono::seconds_double sec_350 = std::chrono::milliseconds(350);
  ASSERT_DOUBLE_EQ(sec_350.count(), 0.35);

  const utils::chrono::seconds_double sec_1750 =
      std::chrono::milliseconds(1750);
  ASSERT_DOUBLE_EQ(sec_1750.count(), 1.75);

  const utils::chrono::seconds_double sec_neg = std::chrono::milliseconds(-500);
  ASSERT_DOUBLE_EQ(sec_neg.count(), -0.5);
}

TEST(DeviceNotifyChrono, Days) {
  const auto two_days_hours =
      std::chrono::duration_cast<std::chrono::hours>(utils::chrono::days(2));
  ASSERT_EQ(two_days_hours.count(), 48);

  const auto one_day =
      std::chrono::duration_cast<utils::chrono::days>(std::chrono::hours(30));
  ASSERT_EQ(one_day.count(), 1);

  const auto day_zero = std::chrono::duration_cast<utils::chrono::days>(
      std::chrono::milliseconds(100));
  ASSERT_EQ(day_zero.count(), 0);

  const auto day_neg =
      std::chrono::duration_cast<utils::chrono::days>(std::chrono::hours(-48));
  ASSERT_EQ(day_neg.count(), -2);
}

TEST(DeviceNotifyChrono, DaysRound) {
  utils::chrono::days days_round;
  days_round =
      std::chrono::duration_cast<utils::chrono::days>(std::chrono::hours(-47));
  ASSERT_EQ(days_round.count(), -1);

  days_round =
      std::chrono::duration_cast<utils::chrono::days>(std::chrono::hours(-49));
  ASSERT_EQ(days_round.count(), -2);

  days_round =
      std::chrono::duration_cast<utils::chrono::days>(std::chrono::hours(47));
  ASSERT_EQ(days_round.count(), 1);

  days_round =
      std::chrono::duration_cast<utils::chrono::days>(std::chrono::hours(49));
  ASSERT_EQ(days_round.count(), 2);
}

TEST(DeviceNotifyChrono, RetryAfter) {
  using utils::chrono::ParseRetryAfter;
  utils::chrono::optional_milliseconds result;
  const auto now = utils::datetime::Stringtime("1994-11-06 08:49:37", "UTC",
                                               "%Y-%m-%d %H:%M:%S");
  // bad strings
  ASSERT_FALSE(ParseRetryAfter("", now).has_value());
  ASSERT_FALSE(ParseRetryAfter("bla-bla-bla", now).has_value());
  ASSERT_FALSE(ParseRetryAfter("Mon Mon Mon", now).has_value());
  // invalid numbers
  ASSERT_FALSE(ParseRetryAfter("0", now).has_value());
  ASSERT_FALSE(ParseRetryAfter("-1", now).has_value());
  ASSERT_FALSE(ParseRetryAfter("123 456", now).has_value());
  // Valid numbers
  result = ParseRetryAfter(" 120 ", now);
  ASSERT_TRUE(result.has_value());
  EXPECT_EQ(*result, std::chrono::seconds(120));
  // Valid time
  result = ParseRetryAfter(" Sun, 06 Nov 1994 08:49:37 GMT ", now);
  ASSERT_TRUE(result.has_value());
  std::cout << "result=" << result->count() << std::endl;
  EXPECT_EQ(*result, std::chrono::seconds(0));
  result = ParseRetryAfter(" Sun, 06 Nov 1994 08:49:47 GMT ", now);
  ASSERT_TRUE(result.has_value());
  std::cout << "result=" << result->count() << std::endl;
  EXPECT_EQ(*result, std::chrono::seconds(10));
  // Time in the past
  result = ParseRetryAfter(" Sun, 06 Nov 1994 08:49:27 GMT ", now);
  ASSERT_TRUE(result.has_value());
  EXPECT_EQ(*result, std::chrono::milliseconds(0));
}
