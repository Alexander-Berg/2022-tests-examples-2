#include <gtest/gtest.h>

#include <userver/utils/datetime.hpp>
#include <utils/time.hpp>

namespace loyalty {

namespace ud = ::utils::datetime;
namespace lu = loyalty::utils;

namespace {

std::string Timestring(const std::chrono::system_clock::time_point& time) {
  return ud::Timestring(time, "UTC", "%Y-%m-%d %H:%M:%S");
}

}  // namespace

TEST(GetStartOfPeriodTest, Time) {
  const auto& feb =
      ud::Stringtime("2019-02-28 21:00:00", "UTC", "%Y-%m-%d %H:%M:%S");
  EXPECT_EQ(Timestring(lu::GetStartOfPeriod(feb)), "2019-01-31 21:00:00");

  const auto& jan =
      ud::Stringtime("2019-01-31 21:00:00", "UTC", "%Y-%m-%d %H:%M:%S");
  EXPECT_EQ(Timestring(lu::GetStartOfPeriod(jan)), "2018-12-31 21:00:00");
}

TEST(GetEndOfPeriodTest, Time) {
  const auto& feb =
      ud::Stringtime("2019-02-12 12:12:12", "UTC", "%Y-%m-%d %H:%M:%S");
  EXPECT_EQ(Timestring(lu::GetEndOfPeriod(feb)), "2019-02-28 21:00:00");

  const auto& dec =
      ud::Stringtime("2018-12-12 12:12:12", "UTC", "%Y-%m-%d %H:%M:%S");
  EXPECT_EQ(Timestring(lu::GetEndOfPeriod(dec)), "2018-12-31 21:00:00");
}

TEST(GetCountWindowTest, Time) {
  const auto& feb =
      ud::Stringtime("2019-02-12 12:12:12", "UTC", "%Y-%m-%d %H:%M:%S");
  EXPECT_EQ(Timestring(lu::GetCountWindow(feb)), "2018-12-31 21:00:00");

  const auto& dec =
      ud::Stringtime("2020-01-01 01:01:00", "UTC", "%Y-%m-%d %H:%M:%S");
  EXPECT_EQ(Timestring(lu::GetCountWindow(dec)), "2019-12-31 21:00:00");
}

TEST(GetDateMonthTest, Time) {
  const auto& feb =
      ud::Stringtime("2019-02-06 12:12:12", "UTC", "%Y-%m-%d %H:%M:%S");
  EXPECT_EQ(lu::GetDateMonth(feb), "feb");

  const auto& dec =
      ud::Stringtime("2019-12-31 12:12:12", "UTC", "%Y-%m-%d %H:%M:%S");
  EXPECT_EQ(lu::GetDateMonth(dec), "dec");
}

}  // namespace loyalty
