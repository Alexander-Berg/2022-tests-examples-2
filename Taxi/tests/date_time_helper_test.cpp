#include <gtest/gtest.h>

#include <userver/utils/datetime.hpp>
#include "helpers/date_time_helper.hpp"

#include <fmt/format.h>

using DateTimeHelper = eats_performer_shifts::helpers::DateTimeHelper;

TEST(DateTimeHelper, GetUtcTimeMoscow) {
  const auto& time = DateTimeHelper::GetUtcTime(
      utils::datetime::Stringtime("2021-08-05T23:00:00+0000"),
      DateTimeHelper::kMoscowTimeZone, "10:00");

  ASSERT_EQ(utils::datetime::Stringtime("2021-08-06T07:00:00+0000"), time);
}

TEST(DateTimeHelper, GetUtcTimeShangai) {
  const auto& time = DateTimeHelper::GetUtcTime(
      utils::datetime::Stringtime("2021-08-05T18:00:00+0000"), "Asia/Shanghai",
      "10:00");  // utc+8

  ASSERT_EQ(utils::datetime::Stringtime("2021-08-06T02:00:00+0000"), time);
}

TEST(DateTimeHelper, GetUtcTimeNewYork) {
  const auto& time = DateTimeHelper::GetUtcTime(
      utils::datetime::Stringtime("2021-08-05T03:00:00+0000"),
      "America/New_York", "10:00");  // utc-4

  ASSERT_EQ(utils::datetime::Stringtime("2021-08-04T14:00:00+0000"), time);
}

TEST(DateTimeHelper, GetDateFromTimePointCheckMoscowOffsetOnTopBorder) {
  const auto& time = DateTimeHelper::GetDateFromTimePoint(
      utils::datetime::Stringtime("2021-08-05T23:59:00+0300"));

  ASSERT_EQ(utils::datetime::Date(2021, 8, 5), time);
}

TEST(DateTimeHelper, GetDateFromTimePointCheckMoscowOffsetBottomBorder) {
  auto time = ::utils::datetime::Stringtime("2021-06-17T00:00:00+0300");
  auto date = DateTimeHelper::GetDateFromTimePoint(time);

  ASSERT_EQ(::utils::datetime::ToString(date), "2021-06-16");
}

TEST(DateTimeHelper, GetDateFromTimePointRandomAmerica) {
  auto time = ::utils::datetime::Stringtime(
      "2021-06-17T21:00:00-0400");  // utc-4 "America/New_York"
  auto date = DateTimeHelper::GetDateFromTimePoint(time);

  ASSERT_EQ(::utils::datetime::ToString(date), "2021-06-18");
}

TEST(DateTimeHelper, GetDateFromTimePointRandomAsia) {
  auto time = ::utils::datetime::Stringtime(
      "2021-06-17T07:00:00+0800");  // utc+8 "Asia/Shanghai",
  auto date =
      eats_performer_shifts::helpers::DateTimeHelper::GetDateFromTimePoint(
          time);

  ASSERT_EQ(::utils::datetime::ToString(date), "2021-06-16");
}

TEST(DateTimeHelper, ModifyTimePointToWeeksAndWeekdayWithoutPlusWeek) {
  auto time =
      ::utils::datetime::Stringtime("2022-04-14T07:00:00+0300");  // utc+3

  const auto& result = DateTimeHelper::ModifyTimePointToWeeksAndWeekday(
      time, 0, cctz::weekday::wednesday, DateTimeHelper::kMoscowTimeZone);

  ASSERT_EQ(::utils::datetime::Stringtime("2022-04-20T04:00:00+0000"), result);
}

TEST(DateTimeHelper, ModifyTimePointToWeeksAndWeekdayWithPlusWeek) {
  auto time =
      ::utils::datetime::Stringtime("2022-04-14T07:00:00+0300");  // utc+3

  const auto& result = DateTimeHelper::ModifyTimePointToWeeksAndWeekday(
      time, 1, cctz::weekday::wednesday, DateTimeHelper::kMoscowTimeZone);

  ASSERT_EQ(::utils::datetime::Stringtime("2022-04-27T04:00:00+0000"), result);
}

TEST(DateTimeHelper, ModifyTimePointToWeeksAndWeekdayWithMinusWeek) {
  auto time =
      ::utils::datetime::Stringtime("2022-04-14T07:00:00+0300");  // utc+3

  const auto& result = DateTimeHelper::ModifyTimePointToWeeksAndWeekday(
      time, -1, cctz::weekday::wednesday, DateTimeHelper::kMoscowTimeZone);

  ASSERT_EQ(::utils::datetime::Stringtime("2022-04-13T04:00:00+0000"), result);
}

TEST(DateTimeHelper, ModifyTimePointToWeeksAndWeekdakIfTryFindToday) {
  auto time =
      ::utils::datetime::Stringtime("2022-04-14T07:00:00+0300");  // utc+3

  const auto& result = DateTimeHelper::ModifyTimePointToWeeksAndWeekday(
      time, 0, cctz::weekday::thursday, DateTimeHelper::kMoscowTimeZone);

  ASSERT_EQ(::utils::datetime::Stringtime("2022-04-21T04:00:00+0000"), result);
}
