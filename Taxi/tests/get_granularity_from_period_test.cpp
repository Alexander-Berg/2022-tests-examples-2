#include <userver/utest/utest.hpp>

#include <utils/get_granularity_from_period.hpp>

namespace eats_report_storage::utils {

TEST(GranularityDetermination,
     function_should_return_day_for_period_of_one_day) {
  auto from = ::utils::datetime::Stringtime(
      "2001-01-11", ::utils::datetime::kDefaultTimezone, "%Y-%m-%d");
  auto to = ::utils::datetime::Stringtime(
      "2001-01-12", ::utils::datetime::kDefaultTimezone, "%Y-%m-%d");
  ASSERT_EQ(GetGranularityFromPeriod(from, to), types::GroupBy::kDay);
}

TEST(GranularityDetermination,
     function_should_return_day_for_period_of_one_week) {
  auto from = ::utils::datetime::Stringtime(
      "2001-01-11", ::utils::datetime::kDefaultTimezone, "%Y-%m-%d");
  auto to = ::utils::datetime::Stringtime(
      "2001-01-18", ::utils::datetime::kDefaultTimezone, "%Y-%m-%d");
  ASSERT_EQ(GetGranularityFromPeriod(from, to), types::GroupBy::kDay);
}

TEST(GranularityDetermination,
     function_should_return_week_for_period_longer_then_week) {
  auto from = ::utils::datetime::Stringtime(
      "2001-01-11", ::utils::datetime::kDefaultTimezone, "%Y-%m-%d");
  auto to = ::utils::datetime::Stringtime(
      "2001-01-19", ::utils::datetime::kDefaultTimezone, "%Y-%m-%d");
  ASSERT_EQ(GetGranularityFromPeriod(from, to), types::GroupBy::kWeek);
}

TEST(GranularityDetermination,
     function_should_return_week_for_period_of_one_month) {
  auto from = ::utils::datetime::Stringtime(
      "2001-01-11", ::utils::datetime::kDefaultTimezone, "%Y-%m-%d");
  auto to = ::utils::datetime::Stringtime(
      "2001-02-11", ::utils::datetime::kDefaultTimezone, "%Y-%m-%d");
  ASSERT_EQ(GetGranularityFromPeriod(from, to), types::GroupBy::kWeek);
}

TEST(GranularityDetermination,
     function_should_return_day_for_period_longer_then_month) {
  auto from = ::utils::datetime::Stringtime(
      "2001-01-11", ::utils::datetime::kDefaultTimezone, "%Y-%m-%d");
  auto to = ::utils::datetime::Stringtime(
      "2001-02-12", ::utils::datetime::kDefaultTimezone, "%Y-%m-%d");
  ASSERT_EQ(GetGranularityFromPeriod(from, to), types::GroupBy::kMonth);
}

}  // namespace eats_report_storage::utils
