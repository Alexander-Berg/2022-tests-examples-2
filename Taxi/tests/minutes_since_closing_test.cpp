#include <gtest/gtest.h>

#include <grocery-shared/datetime/timetable.hpp>

#include "common.hpp"

using namespace grocery_shared::datetime;
using namespace std::chrono_literals;

TEST(MinutesSinceClosing, friday_with_shifts_in_first_gap) {
  const auto timetable = test::ConstructTimetable(
      {{Day::kFriday, "01:00", "01:58"},
       {Day::kFriday, "03:00", "04:00"},
       {Day::kFriday, "23:00", "10:00"}});  // end on Saturday
  const auto time_moscow_02_00 = test::GetMomentInUTC(2020, 5, 14, 23, 00);

  const auto res =
      timetable.MinutesSinceClosing(time_moscow_02_00, test::kMoscowTimezone);

  EXPECT_EQ(test::GetWeekDay(time_moscow_02_00, test::kMoscowTimezone),
            cctz::weekday::friday);
  ASSERT_TRUE(res.has_value());
  const std::chrono::minutes expected = 2min;
  ASSERT_EQ(res->count(), expected.count());
}

TEST(MinutesSinceClosing, friday_with_shifts_in_second_gap) {
  const auto timetable = test::ConstructTimetable(
      {{Day::kFriday, "01:00", "02:00"},
       {Day::kFriday, "03:00", "03:58"},
       {Day::kFriday, "23:00", "10:00"}});  // end on Saturday
  const auto time_moscow_04_00 = test::GetMomentInUTC(2020, 5, 15, 01, 00);

  const auto res =
      timetable.MinutesSinceClosing(time_moscow_04_00, test::kMoscowTimezone);

  EXPECT_EQ(test::GetWeekDay(time_moscow_04_00, test::kMoscowTimezone),
            cctz::weekday::friday);
  ASSERT_TRUE(res.has_value());
  const std::chrono::minutes expected = 2min;
  ASSERT_EQ(res->count(), expected.count());
}

TEST(MinutesSinceClosing, friday_53_seconds_since_the_first_shift) {
  const auto timetable =
      test::ConstructTimetable({{Day::kFriday, "00:00", "12:14"},
                                {Day::kFriday, "12:30", "21:00"},
                                {Day::kEveryday, "00:00", "23:30"}});
  const auto time_moscow_12_14_53 =
      test::GetMomentInUTC(2020, 5, 15, 9, 14, 53);

  const auto res = timetable.MinutesSinceClosing(time_moscow_12_14_53,
                                                 test::kMoscowTimezone);

  EXPECT_EQ(test::GetWeekDay(time_moscow_12_14_53, test::kMoscowTimezone),
            cctz::weekday::friday);
  ASSERT_TRUE(res.has_value());
  const std::chrono::minutes expected = 0min;
  ASSERT_EQ(res->count(), expected.count());
}

TEST(MinutesSinceClosing, friday_with_shifts_in_third_gap_split) {
  const auto timetable = test::ConstructTimetable(
      {{Day::kFriday, "01:00", "02:00"},
       {Day::kFriday, "03:00", "04:00"},
       {Day::kFriday, "23:00", "09:58"}});  // end on Saturday
  const auto time_moscow_10_00 = test::GetMomentInUTC(2020, 5, 16, 7, 00);

  const auto res =
      timetable.MinutesSinceClosing(time_moscow_10_00, test::kMoscowTimezone);

  EXPECT_EQ(test::GetWeekDay(time_moscow_10_00, test::kMoscowTimezone),
            cctz::weekday::saturday);
  ASSERT_TRUE(res.has_value());
  const std::chrono::minutes expected = 2min;
  ASSERT_EQ(res->count(), expected.count());
}

TEST(MinutesSinceClosing, friday_with_shifts_in_third_gap_split_v2) {
  const auto timetable = test::ConstructTimetable(
      {{Day::kFriday, "10:00", "11:00"},
       {Day::kFriday, "23:00", "01:58"}});  // end on Saturday
  const auto time_moscow_03_00 = test::GetMomentInUTC(2020, 5, 16, 0, 00);

  const auto res =
      timetable.MinutesSinceClosing(time_moscow_03_00, test::kMoscowTimezone);

  EXPECT_EQ(test::GetWeekDay(time_moscow_03_00, test::kMoscowTimezone),
            cctz::weekday::saturday);
  ASSERT_TRUE(res.has_value());
  const std::chrono::minutes expected = 1h + 2min;
  ASSERT_EQ(res->count(), expected.count());
}

TEST(MinutesSinceClosing, friday_with_shifts_in_third_gap) {
  const auto timetable =
      test::ConstructTimetable({{Day::kFriday, "01:00", "02:00"},
                                {Day::kFriday, "03:00", "03:58"},
                                {Day::kFriday, "22:00", "23:00"}});
  const auto time_moscow_05_00 = test::GetMomentInUTC(2020, 5, 15, 02, 00);

  const auto res =
      timetable.MinutesSinceClosing(time_moscow_05_00, test::kMoscowTimezone);

  EXPECT_EQ(test::GetWeekDay(time_moscow_05_00, test::kMoscowTimezone),
            cctz::weekday::friday);
  ASSERT_TRUE(res.has_value());
  const std::chrono::minutes expected = 1h + 2min;
  ASSERT_EQ(res->count(), expected.count());
}

TEST(MinutesSinceClosing, friday) {
  const auto timetable =
      test::ConstructTimetable({{Day::kFriday, "09:00", "23:00"}});
  const auto time_moscow_23_01 = test::GetMomentInUTC(2020, 5, 15, 20, 01);

  const auto res =
      timetable.MinutesSinceClosing(time_moscow_23_01, test::kMoscowTimezone);

  EXPECT_EQ(test::GetWeekDay(time_moscow_23_01, test::kMoscowTimezone),
            cctz::weekday::friday);
  ASSERT_TRUE(res.has_value());
  const std::chrono::minutes expected = 1min;
  ASSERT_EQ(res->count(), expected.count());
}

TEST(MinutesSinceClosing, friday_close_at24_on_next_day) {
  const auto timetable =
      test::ConstructTimetable({{Day::kFriday, "09:00", "24:00"}});
  const auto time_moscow_00_01 = test::GetMomentInUTC(2020, 5, 15, 21, 01);

  const auto res =
      timetable.MinutesSinceClosing(time_moscow_00_01, test::kMoscowTimezone);

  EXPECT_EQ(test::GetWeekDay(time_moscow_00_01, test::kMoscowTimezone),
            cctz::weekday::saturday);
  const std::chrono::minutes expected = 1min;
  ASSERT_EQ(res->count(), expected.count());
}

TEST(MinutesSinceClosing, friday_now_on_next_day) {
  const auto timetable =
      test::ConstructTimetable({{Day::kFriday, "09:00", "23:00"}});
  const auto time_moscow_00_01 = test::GetMomentInUTC(2020, 5, 15, 21, 01);

  const auto res =
      timetable.MinutesSinceClosing(time_moscow_00_01, test::kMoscowTimezone);

  EXPECT_EQ(test::GetWeekDay(time_moscow_00_01, test::kMoscowTimezone),
            cctz::weekday::saturday);
  ASSERT_TRUE(res.has_value());
  const std::chrono::minutes expected = 1h + 1min;
  ASSERT_EQ(res->count(), expected.count());
}

TEST(MinutesSinceClosing, closing_week_ago) {
  const auto timetable =
      test::ConstructTimetable({{Day::kFriday, "09:00", "23:00"}});
  const auto time_moscow_03_01 = test::GetMomentInUTC(2020, 5, 22, 0, 01);

  const auto res =
      timetable.MinutesSinceClosing(time_moscow_03_01, test::kMoscowTimezone);

  EXPECT_EQ(test::GetWeekDay(time_moscow_03_01, test::kMoscowTimezone),
            cctz::weekday::friday);
  ASSERT_TRUE(res.has_value());
  const std::chrono::minutes expected = 4h + 24h * 6 + 1min;
  ASSERT_EQ(res->count(), expected.count());
}

TEST(MinutesSinceClosing, closing_week_ago_v2) {
  const auto timetable =
      test::ConstructTimetable({{Day::kFriday, "04:00", "05:00"}});
  const auto time_moscow_03_01 = test::GetMomentInUTC(2020, 5, 22, 0, 01);

  const auto res =
      timetable.MinutesSinceClosing(time_moscow_03_01, test::kMoscowTimezone);

  EXPECT_EQ(test::GetWeekDay(time_moscow_03_01, test::kMoscowTimezone),
            cctz::weekday::friday);
  ASSERT_TRUE(res.has_value());
  const std::chrono::minutes expected = 22h + 24h * 6 + 1min;
  ASSERT_EQ(res->count(), expected.count());
}

TEST(MinutesSinceClosing, closing_5_days_ago) {
  const auto timetable = test::ConstructTimetable(
      {{Day::kFriday, "09:00", "01:00"}});  // end on Saturday
  const auto time_moscow_03_01 = test::GetMomentInUTC(2020, 5, 22, 0, 01);

  const auto res =
      timetable.MinutesSinceClosing(time_moscow_03_01, test::kMoscowTimezone);

  EXPECT_EQ(test::GetWeekDay(time_moscow_03_01, test::kMoscowTimezone),
            cctz::weekday::friday);
  ASSERT_TRUE(res.has_value());
  const std::chrono::minutes expected = 2h + 24h * 6 + 1min;
  ASSERT_EQ(res->count(), expected.count());
}

TEST(MinutesSinceClosing, friday_split_now_on_next_day) {
  const auto timetable = test::ConstructTimetable(
      {{Day::kFriday, "20:00", "10:00"}});  // end on Saturday
  const auto time_moscow_10_01 = test::GetMomentInUTC(2020, 5, 16, 7, 01);

  const auto res =
      timetable.MinutesSinceClosing(time_moscow_10_01, test::kMoscowTimezone);

  EXPECT_EQ(test::GetWeekDay(time_moscow_10_01, test::kMoscowTimezone),
            cctz::weekday::saturday);
  ASSERT_TRUE(res.has_value());
  const std::chrono::minutes expected = 1min;
  ASSERT_EQ(res->count(), expected.count());
}

TEST(MinutesSinceClosing, friday_split_now_on_next_next_day) {
  const auto timetable = test::ConstructTimetable(
      {{Day::kFriday, "20:00", "10:00"}});  // end on Saturday

  const auto time_moscow_10_01 = test::GetMomentInUTC(2020, 5, 17, 7, 01);
  const auto res =
      timetable.MinutesSinceClosing(time_moscow_10_01, test::kMoscowTimezone);

  EXPECT_EQ(test::GetWeekDay(time_moscow_10_01, test::kMoscowTimezone),
            cctz::weekday::sunday);
  ASSERT_TRUE(res.has_value());
  const std::chrono::minutes expected = 24h + 1min;
  ASSERT_EQ(res->count(), expected.count());
}

TEST(MinutesSinceClosing, friday_split_availeble) {
  const auto timetable = test::ConstructTimetable(
      {{Day::kFriday, "20:00", "10:00"}});  // end on Saturday
  const auto time_moscow_09_59 = test::GetMomentInUTC(2020, 5, 16, 6, 59);

  const auto res =
      timetable.MinutesSinceClosing(time_moscow_09_59, test::kMoscowTimezone);

  EXPECT_EQ(test::GetWeekDay(time_moscow_09_59, test::kMoscowTimezone),
            cctz::weekday::saturday);
  ASSERT_FALSE(res.has_value());
}

TEST(MinutesSinceClosing, everyday_now_on_next_day) {
  const auto timetable =
      test::ConstructTimetable({{Day::kEveryday, "09:00", "23:00"}});
  const auto time_moscow_00_01 = test::GetMomentInUTC(2020, 5, 15, 21, 01);

  const auto res =
      timetable.MinutesSinceClosing(time_moscow_00_01, test::kMoscowTimezone);

  EXPECT_EQ(test::GetWeekDay(time_moscow_00_01, test::kMoscowTimezone),
            cctz::weekday::saturday);
  ASSERT_TRUE(res.has_value());
  const std::chrono::minutes expected = 1h + 1min;
  ASSERT_EQ(res->count(), expected.count());
}

TEST(MinutesSinceClosing, null_minutes_since_closing) {
  const auto timetable =
      test::ConstructTimetable({{Day::kEveryday, "09:00", "23:00"}});
  const auto time_moscow_23_00_59 =
      test::GetMomentInUTC(2020, 5, 15, 20, 00, 59);

  const auto res = timetable.MinutesSinceClosing(time_moscow_23_00_59,
                                                 test::kMoscowTimezone);

  EXPECT_EQ(test::GetWeekDay(time_moscow_23_00_59, test::kMoscowTimezone),
            cctz::weekday::friday);
  ASSERT_TRUE(res.has_value());
  const std::chrono::minutes expected = 0min;
  ASSERT_EQ(res->count(), expected.count());
}

TEST(MinutesSinceClosing, everyday_now_on_this_day) {
  const auto timetable =
      test::ConstructTimetable({{Day::kEveryday, "09:00", "23:00"}});
  const auto time_moscow_23_15 = test::GetMomentInUTC(2020, 5, 15, 20, 15);

  const auto res =
      timetable.MinutesSinceClosing(time_moscow_23_15, test::kMoscowTimezone);

  EXPECT_EQ(test::GetWeekDay(time_moscow_23_15, test::kMoscowTimezone),
            cctz::weekday::friday);
  ASSERT_TRUE(res.has_value());
  const std::chrono::minutes expected = 15min;
  ASSERT_EQ(res->count(), expected.count());
}

TEST(MinutesSinceClosing, work_2_days_now_on_second_day) {
  const auto timetable = test::ConstructTimetable(
      {{Day::kMonday, "09:00", "22:00"}, {Day::kTuesday, "09:00", "23:00"}});
  const auto time_moscow_23_15 = test::GetMomentInUTC(2020, 5, 12, 20, 15);

  const auto res =
      timetable.MinutesSinceClosing(time_moscow_23_15, test::kMoscowTimezone);

  EXPECT_EQ(test::GetWeekDay(time_moscow_23_15, test::kMoscowTimezone),
            cctz::weekday::tuesday);
  ASSERT_TRUE(res.has_value());
  const std::chrono::minutes expected = 15min;
  ASSERT_EQ(res->count(), expected.count());
}

TEST(MinutesSinceClosing, work_2_days_now_on_first) {
  const auto timetable = test::ConstructTimetable(
      {{Day::kMonday, "09:00", "22:00"}, {Day::kTuesday, "09:00", "23:00"}});
  const auto time_moscow_23_15 = test::GetMomentInUTC(2020, 5, 11, 20, 15);

  const auto res =
      timetable.MinutesSinceClosing(time_moscow_23_15, test::kMoscowTimezone);

  EXPECT_EQ(test::GetWeekDay(time_moscow_23_15, test::kMoscowTimezone),
            cctz::weekday::monday);
  ASSERT_TRUE(res.has_value());
  const std::chrono::minutes expected = 1h + 15min;
  ASSERT_EQ(res->count(), expected.count());
}
