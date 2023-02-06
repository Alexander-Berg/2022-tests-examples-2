#include <userver/utest/utest.hpp>

#include "build_default_test.hpp"

#include <core/context/zone/category_helpers.hpp>
#include <userver/utils/mock_now.hpp>

namespace routestats::core {

using DayType = MinimalPrice::DayType;

bool IsWeekend(const models::Country& country, const std::string& tz,
               const std::chrono::system_clock::time_point& timestamp);
bool IsMatchedCategoryType(MinimalPrice::CategoryType category_type);
bool IsMatchedDayType(bool is_weekend, DayType day_type);
std::pair<int, int> SplitTime(const std::chrono::minutes& minutes);
bool IsMatchedTimeInterval(const MinimalPrice& price, const std::string& tz,
                           const std::chrono::system_clock::time_point& now);

void TestIsWeekend(int timestamp, std::string tz, bool expected) {
  const auto now =
      std::chrono::system_clock::time_point(std::chrono::seconds(timestamp));
  auto country = BuildDefaultCountry();
  country.holidays = std::unordered_set<std::string>{"2020-11-04"};
  country.workdays = std::unordered_set<std::string>{"2020-11-01"};
  ASSERT_EQ(IsWeekend(country, tz, now), expected);
}

// monday early morning 0:45
TEST(IsWeekend, Workday) { TestIsWeekend(1604871900, "Europe/Moscow", false); }

// saturday early morning 0:45, not weekend yet
TEST(IsWeekend, WorkdayTZ) {
  TestIsWeekend(1604699100, "Europe/Helsinki", false);
}

// sunday late evening 23:45
TEST(IsWeekend, Weekend) { TestIsWeekend(1604868300, "Europe/Moscow", true); }

// monday early morning 0:45, still weekend
TEST(IsWeekend, WeekendTZ) {
  TestIsWeekend(1604871900, "Europe/Helsinki", true);
}

TEST(IsWeekend, WeekendSpecial) {
  TestIsWeekend(1604492100, "Europe/Moscow", true);
}

TEST(IsWeekend, WorkdaySpecial) {
  TestIsWeekend(1604232900, "Europe/Moscow", false);
}

TEST(IsMatchedCategoryType, Match) {
  ASSERT_TRUE(IsMatchedCategoryType(MinimalPrice::CategoryType(0)));
}

TEST(IsMatchedCategoryType, NotMatch) {
  ASSERT_FALSE(IsMatchedCategoryType(MinimalPrice::CategoryType(1)));
}

void TestIsMatchedDayType(bool is_weekend, DayType day_type, bool expected) {
  ASSERT_EQ(IsMatchedDayType(is_weekend, day_type), expected);
}

TEST(IsMatchedDayType, EveryDay) {
  TestIsMatchedDayType(false, DayType::kEveryday, true);
}

TEST(IsMatchedDayType, MatchWorkday) {
  TestIsMatchedDayType(false, DayType::kWorkday, true);
}

TEST(IsMatchedDayType, MatchWeekend) {
  TestIsMatchedDayType(true, DayType::kWeekend, true);
}

TEST(IsMatchedDayType, NotMatchWorkday) {
  TestIsMatchedDayType(true, DayType::kWorkday, false);
}

TEST(IsMatchedDayType, NotMatchWeekend) {
  TestIsMatchedDayType(false, DayType::kWeekend, false);
}

TEST(SplitTime, HappyPath) {
  auto result = SplitTime(std::chrono::minutes(1234));
  ASSERT_EQ(result.first, 20);
  ASSERT_EQ(result.second, 34);
}

void TestIsMatchedTimeInterval(int timestamp, std::string tz, bool expected) {
  const auto now =
      std::chrono::system_clock::time_point(std::chrono::seconds(timestamp));
  const auto price = BuildDefaultMinimalPrice();
  ASSERT_EQ(IsMatchedTimeInterval(price, tz, now), expected);
}

// 9:15
TEST(IsMatchedTimeInterval, NoMatchTZ) {
  TestIsMatchedTimeInterval(1604211300, "Europe/Helsinki", false);
}

// 18:15
TEST(IsMatchedTimeInterval, MatchTZ) {
  TestIsMatchedTimeInterval(1604243700, "Europe/Helsinki", true);
}

// 9:15
TEST(IsMatchedTimeInterval, Match) {
  TestIsMatchedTimeInterval(1604211300, "Europe/Moscow", true);
}

// 18:15
TEST(IsMatchedTimeInterval, NoMatch) {
  TestIsMatchedTimeInterval(1604243700, "Europe/Moscow", false);
}

}  // namespace routestats::core
