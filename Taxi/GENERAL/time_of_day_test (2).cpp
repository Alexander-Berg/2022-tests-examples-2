#include <userver/logging/log.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/datetime.hpp>

#include <datetime/time_of_day.hpp>

using Time = grocery_depots::datetime::Time;

TEST(Time, FromHHMMInt) {
  EXPECT_EQ(0, Time::FromHHMMInt(0).GetMinutesSinceMidnight().count());
  EXPECT_EQ(59, Time::FromHHMMInt(59).GetMinutesSinceMidnight().count());
  EXPECT_EQ(60, Time::FromHHMMInt(100).GetMinutesSinceMidnight().count());
  EXPECT_EQ(7 * 60 + 30,
            Time::FromHHMMInt(730).GetMinutesSinceMidnight().count());
}

TEST(Time, FromHHMMString) {
  EXPECT_EQ(0, Time::FromHHMMString("00:00").GetMinutesSinceMidnight().count());
  EXPECT_EQ(59,
            Time::FromHHMMString("00:59").GetMinutesSinceMidnight().count());
  EXPECT_EQ(60,
            Time::FromHHMMString("01:00").GetMinutesSinceMidnight().count());
  EXPECT_EQ(7 * 60 + 30,
            Time::FromHHMMString("7:30").GetMinutesSinceMidnight().count());
}

Time FromMinutesSinceMidnight(int c) {
  return Time::FromMinutesSinceMidnight(std::chrono::minutes(c));
}

TEST(Time, FromMinutesSinceMidnight) {
  EXPECT_EQ(0, FromMinutesSinceMidnight(0).GetMinutesSinceMidnight().count());
  EXPECT_EQ(59, FromMinutesSinceMidnight(59).GetMinutesSinceMidnight().count());
  EXPECT_EQ(60, FromMinutesSinceMidnight(60).GetMinutesSinceMidnight().count());
}

TEST(MakeTimePoint, Zero) {
  auto time = Time::FromHHMMInt(730);

  auto tz = cctz::local_time_zone();

  std::tm tm{};
  tm.tm_min = 30;
  tm.tm_hour = 7;
  tm.tm_year = 71;
  tm.tm_mon = 1;
  tm.tm_mday = 4;

  auto tp = time.MakeTimePoint(cctz::civil_day{1971, 2, 4}, tz);

  auto tp2 = std::chrono::system_clock::from_time_t(std::mktime(&tm));

  EXPECT_EQ(tp, tp2);
}
