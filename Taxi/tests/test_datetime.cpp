#include <cctz/civil_time_detail.h>
#include <ctime>
#include <userver/utils/datetime.hpp>

#include "common/utils/time.hpp"

#include <userver/utest/utest.hpp>

TEST(DateTimeTest, civil_time_Test) {
  const auto t = ::utils::datetime::Stringtime("2020-01-10T23:15:55Z", "UTC");

  const std::string tz1 = "UTC";
  const std::string tz2 = "Europe/Moscow";
  const std::string tz3 = "Asia/Yekaterinburg";

  auto t1 = utils::datetime::Localize(t, tz1);
  auto t2 = utils::datetime::Localize(t, tz2);
  auto t3 = utils::datetime::Localize(t, tz3);
  EXPECT_EQ(t1.second(), 55);
  EXPECT_EQ(t1.minute(), 15);
  EXPECT_EQ(t1.hour(), 23);
  EXPECT_EQ(t1.day(), 10);
  EXPECT_EQ(t1.month(), 1);
  EXPECT_EQ(t1.year(), 2020);

  EXPECT_EQ(t2.second(), 55);
  EXPECT_EQ(t2.minute(), 15);
  EXPECT_EQ(t2.hour(), 2);  // UTC+3
  EXPECT_EQ(t2.day(), 11);
  EXPECT_EQ(t2.month(), 1);
  EXPECT_EQ(t2.year(), 2020);

  EXPECT_EQ(t3.second(), 55);
  EXPECT_EQ(t3.minute(), 15);
  EXPECT_EQ(t3.hour(), 4);  // UTC+5
  EXPECT_EQ(t3.day(), 11);
  EXPECT_EQ(t3.month(), 1);
  EXPECT_EQ(t3.year(), 2020);
}

TEST(DateTimeTest, daystart_Test) {
  /*
   * 2020-01-10 20:15:55 UTC -> 2020-01-10 UTC -> 2020-01-10 00:00:00 UTC
   * 2020-01-10 23:15:55 Europe/Moscow -> 2020-01-10 MSK ->  2020-01-09 21:00:00
   * UTC 2020-01-11 01:15:55 Asia/Yekaterinburg -> 2020-01-11 YEKT -> 2020-01-10
   * 19:00:00 UTC
   */
  const auto t = ::utils::datetime::Stringtime("2020-01-10T20:15:55Z", "UTC");
  const auto rt1 = ::utils::datetime::Stringtime("2020-01-10T00:00:00Z", "UTC");
  const auto rt2 = ::utils::datetime::Stringtime("2020-01-09T21:00:00Z", "UTC");
  const auto rt3 = ::utils::datetime::Stringtime("2020-01-10T19:00:00Z", "UTC");

  const std::string tz1 = "UTC";
  const std::string tz2 = "Europe/Moscow";
  const std::string tz3 = "Asia/Yekaterinburg";

  const auto t1 = utils::datetime::Localize(t, tz1);
  const auto t2 = utils::datetime::Localize(t, tz2);
  const auto t3 = utils::datetime::Localize(t, tz3);

  const auto d1 = ::cctz::civil_day{t1};
  const auto d2 = ::cctz::civil_day{t2};
  const auto d3 = ::cctz::civil_day{t3};

  const auto u1 = utils::datetime::Unlocalize(d1, tz1);
  const auto u2 = utils::datetime::Unlocalize(d2, tz2);
  const auto u3 = utils::datetime::Unlocalize(d3, tz3);

  const auto dt1 = std::chrono::system_clock::from_time_t(u1);
  const auto dt2 = std::chrono::system_clock::from_time_t(u2);
  const auto dt3 = std::chrono::system_clock::from_time_t(u3);

  EXPECT_EQ(dt1, rt1) << "Failed with " << tz1
                      << " expected: " << utils::datetime::Timestring(rt1)
                      << " actual: " << utils::datetime::Timestring(dt1);
  EXPECT_EQ(dt2, rt2) << "Failed with " << tz2
                      << " expected: " << utils::datetime::Timestring(rt2)
                      << " actual: " << utils::datetime::Timestring(dt2);
  EXPECT_EQ(dt3, rt3) << "Failed with " << tz3
                      << " expected: " << utils::datetime::Timestring(rt3)
                      << " actual: " << utils::datetime::Timestring(dt3);
}

TEST(DateTimeTest, GetLocalStartOfDay_Test) {
  const auto t = ::utils::datetime::Stringtime("2020-01-10T20:15:55Z", "UTC");
  const auto rt1 = ::utils::datetime::Stringtime("2020-01-10T00:00:00Z", "UTC");
  const auto rt2 = ::utils::datetime::Stringtime("2020-01-09T21:00:00Z", "UTC");
  const auto rt3 = ::utils::datetime::Stringtime("2020-01-10T19:00:00Z", "UTC");
  const std::string tz1 = "UTC";
  const std::string tz2 = "Europe/Moscow";
  const std::string tz3 = "Asia/Yekaterinburg";
  const auto dt1 = billing_subventions_x::utils::GetLocalStartOfDay(t, tz1);
  const auto dt2 = billing_subventions_x::utils::GetLocalStartOfDay(t, tz2);
  const auto dt3 = billing_subventions_x::utils::GetLocalStartOfDay(t, tz3);

  EXPECT_EQ(dt1, rt1) << "Failed with " << tz1
                      << " expected: " << utils::datetime::Timestring(rt1)
                      << " actual: " << utils::datetime::Timestring(dt1);
  EXPECT_EQ(dt2, rt2) << "Failed with " << tz2
                      << " expected: " << utils::datetime::Timestring(rt2)
                      << " actual: " << utils::datetime::Timestring(dt2);
  EXPECT_EQ(dt3, rt3) << "Failed with " << tz3
                      << " expected: " << utils::datetime::Timestring(rt3)
                      << " actual: " << utils::datetime::Timestring(dt3);
}
