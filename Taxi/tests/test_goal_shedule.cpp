#include <cctz/civil_time.h>
#include <cctz/time_zone.h>
#include <fmt/format.h>
#include <gtest/gtest.h>
#include <boost/algorithm/string/join.hpp>
#include <boost/range/adaptor/transformed.hpp>

#include <userver/utils/datetime.hpp>
#include <userver/utils/invariant_error.hpp>

#include <clients/billing-subventions-x/definitions.hpp>
#include <subvention-rule-utils/helpers/goal_schedule.hpp>
#include <subvention-rule-utils/models/goal_schedule.hpp>
#include <subvention-rule-utils/models/time_point.hpp>

namespace {

namespace bsx = clients::billing_subventions_x;
namespace sru = subvention_rule_utils;

auto ParseTime(const std::string& timestring) {
  return utils::datetime::Stringtime(timestring);
}

}  // namespace

namespace std {

std::ostream& operator<<(std::ostream& os,
                         const std::optional<sru::models::TimeRange>& range) {
  if (!range) {
    return os << "None";
  }
  return os << fmt::format("({},{})", utils::datetime::Timestring(range->start),
                           utils::datetime::Timestring(range->end));
}

std::ostream& operator<<(std::ostream& os,
                         const sru::models::LocalTimeRange& local_range) {
  return os << "[" << local_range.start << ", " << local_range.end << ")";
}

}  // namespace std

namespace subvention_rule_utils::models {

std::ostream& operator<<(std::ostream& os,
                         sru::models::GoalWeekdaySchedule weekday_schedule) {
  for (const auto& [weekday, schedule] : weekday_schedule) {
    os << weekday << ": ["
       << boost::join(
              schedule | boost::adaptors::transformed(
                             [](const sru::models::DaytimeRange& range) {
                               return ToString(range);
                             }),
              ",")
       << "] ";
  }
  return os;
}

}  // namespace subvention_rule_utils::models

TEST(GoalSchedule, GetNextWindowSinceTimePoint) {
  bsx::ScheduleForGoals schedule_for_goal;

  schedule_for_goal.start = ParseTime("2021-01-10T00:00:00+0000");
  schedule_for_goal.end = ParseTime("2021-01-13T00:00:00+0000");
  schedule_for_goal.window = 3;
  auto now = ParseTime("2021-01-09T13:52:00+0000");
  EXPECT_EQ(sru::helpers::GetNextWindowSinceTimePoint(schedule_for_goal, now),
            std::make_optional(
                sru::models::TimeRange{ParseTime("2021-01-10T00:00:00+0000"),
                                       ParseTime("2021-01-13T00:00:00+0000")}));

  schedule_for_goal.start = ParseTime("2021-01-10T00:00:00+0000");
  schedule_for_goal.end = ParseTime("2021-01-13T00:00:00+0000");
  schedule_for_goal.window = 3;
  now = ParseTime("2021-01-10T00:00:00+0000");
  EXPECT_EQ(sru::helpers::GetNextWindowSinceTimePoint(schedule_for_goal, now),
            std::nullopt);

  schedule_for_goal.start = ParseTime("2021-01-10T00:00:00+0000");
  schedule_for_goal.end = ParseTime("2021-01-19T00:00:00+0000");
  schedule_for_goal.window = 3;
  now = ParseTime("2021-01-12T00:00:00+0000");
  EXPECT_EQ(sru::helpers::GetNextWindowSinceTimePoint(schedule_for_goal, now),
            std::make_optional(
                sru::models::TimeRange{ParseTime("2021-01-13T00:00:00+0000"),
                                       ParseTime("2021-01-16T00:00:00+0000")}));

  schedule_for_goal.start = ParseTime("2021-01-10T00:00:00+0000");
  schedule_for_goal.end = ParseTime("2021-01-13T00:00:00+0000");
  schedule_for_goal.window = 3;
  now = ParseTime("2021-01-13T00:00:00+0000");
  EXPECT_EQ(sru::helpers::GetNextWindowSinceTimePoint(schedule_for_goal, now),
            std::nullopt);
}

TEST(GoalSchedule, GetWindowRangeByNumbers) {
  bsx::ScheduleForGoals schedule_for_goal;

  schedule_for_goal.start = ParseTime("2021-01-10T00:00:00+0000");
  schedule_for_goal.end = ParseTime("2021-01-16T00:00:00+0000");
  schedule_for_goal.window = 3;

  EXPECT_EQ(sru::helpers::GetWindowRangeByNumbers(schedule_for_goal, 3, 4),
            (sru::models::TimeRange{ParseTime("2021-01-19T00:00:00+0000"),
                                    ParseTime("2021-01-22T00:00:00+0000")}));

  EXPECT_EQ(sru::helpers::GetWindowRangeByNumbers(schedule_for_goal, 1, 1),
            (sru::models::TimeRange{ParseTime("2021-01-13T00:00:00+0000"),
                                    ParseTime("2021-01-13T00:00:00+0000")}));

  EXPECT_EQ(sru::helpers::GetWindowRangeByNumbers(schedule_for_goal, 0, 2),
            (sru::models::TimeRange{ParseTime("2021-01-10T00:00:00+0000"),
                                    ParseTime("2021-01-16T00:00:00+0000")}));

  EXPECT_EQ(sru::helpers::GetWindowRangeByNumbers(schedule_for_goal, 0, 3),
            (sru::models::TimeRange{ParseTime("2021-01-10T00:00:00+0000"),
                                    ParseTime("2021-01-19T00:00:00+0000")}));

  EXPECT_EQ(sru::helpers::GetWindowRangeByNumbers(schedule_for_goal, 1, 2),
            (sru::models::TimeRange{ParseTime("2021-01-13T00:00:00+0000"),
                                    ParseTime("2021-01-16T00:00:00+0000")}));
}

TEST(GoalSchedule, GetWindowByNumber) {
  bsx::ScheduleForGoals schedule_for_goal;

  schedule_for_goal.start = ParseTime("2021-01-10T00:00:00+0000");
  schedule_for_goal.end = ParseTime("2021-01-16T00:00:00+0000");
  schedule_for_goal.window = 3;

  EXPECT_EQ(sru::helpers::GetWindowByNumber(schedule_for_goal, 0),
            (sru::models::TimeRange{ParseTime("2021-01-10T00:00:00+0000"),
                                    ParseTime("2021-01-13T00:00:00+0000")}));

  EXPECT_EQ(sru::helpers::GetWindowByNumber(schedule_for_goal, 1),
            (sru::models::TimeRange{ParseTime("2021-01-13T00:00:00+0000"),
                                    ParseTime("2021-01-16T00:00:00+0000")}));

  EXPECT_EQ(sru::helpers::GetWindowByNumber(schedule_for_goal, 2),
            (sru::models::TimeRange{ParseTime("2021-01-16T00:00:00+0000"),
                                    ParseTime("2021-01-19T00:00:00+0000")}));
}

TEST(GoalSchedule, GetWindowsAmount) {
  bsx::ScheduleForGoals schedule_for_goal;

  schedule_for_goal.start = ParseTime("2021-01-10T00:00:00+0000");
  schedule_for_goal.end = ParseTime("2021-01-16T00:00:00+0000");
  schedule_for_goal.window = 3;

  EXPECT_EQ(sru::helpers::GetWindowsAmount(schedule_for_goal), 2);

  schedule_for_goal.window = 1;
  EXPECT_EQ(sru::helpers::GetWindowsAmount(schedule_for_goal), 6);
}

struct BuildWeekdayScheduleForCounterParam {
  std::vector<bsx::GoalScheduleItem> schedule_items;
  std::string counter;
  sru::models::GoalWeekdaySchedule expected;
};

class BuildWeekdayScheduleForCounterFixture
    : public testing::TestWithParam<BuildWeekdayScheduleForCounterParam> {};

TEST_P(BuildWeekdayScheduleForCounterFixture, BuildsAsExpected) {
  const auto actual = sru::models::BuildWeekdayScheduleForCounter(
      GetParam().schedule_items, GetParam().counter);
  EXPECT_EQ(GetParam().expected, actual);
}

INSTANTIATE_TEST_SUITE_P(
    GoalSchedule, BuildWeekdayScheduleForCounterFixture,
    ::testing::Values(

        BuildWeekdayScheduleForCounterParam{{}, "A", {}},

        BuildWeekdayScheduleForCounterParam{
            // schedule items
            {
                {bsx::WeekDay::kMon, "12:00", "A"},
                {bsx::WeekDay::kTue, "11:00", "0"},
            },
            // counter
            "A",
            // expected
            {{cctz::weekday::monday,
              {{sru::models::Daytime(12, 0), sru::models::Daytime(0, 0)}}},
             {cctz::weekday::tuesday,
              {{sru::models::Daytime(0, 0), sru::models::Daytime(11, 0)}}}}},

        BuildWeekdayScheduleForCounterParam{
            // schedule items
            {
                {bsx::WeekDay::kMon, "12:00", "A"},
            },
            // counter
            "A",
            // expected
            {
                {cctz::weekday::monday,
                 {{sru::models::Daytime(12, 0), sru::models::Daytime(0, 0)}}},
                {cctz::weekday::tuesday,
                 {{sru::models::Daytime(0, 0), sru::models::Daytime(0, 0)}}},
                {cctz::weekday::wednesday,
                 {{sru::models::Daytime(0, 0), sru::models::Daytime(0, 0)}}},
                {cctz::weekday::thursday,
                 {{sru::models::Daytime(0, 0), sru::models::Daytime(0, 0)}}},
                {cctz::weekday::friday,
                 {{sru::models::Daytime(0, 0), sru::models::Daytime(0, 0)}}},
                {cctz::weekday::saturday,
                 {{sru::models::Daytime(0, 0), sru::models::Daytime(0, 0)}}},
                {cctz::weekday::sunday,
                 {{sru::models::Daytime(0, 0), sru::models::Daytime(0, 0)}}},
            },
        },

        BuildWeekdayScheduleForCounterParam{
            // schedule items
            {
                {bsx::WeekDay::kMon, "12:00", "A"},
                {bsx::WeekDay::kTue, "00:00", "0"},
                {bsx::WeekDay::kWed, "12:00", "A"},
                {bsx::WeekDay::kThu, "00:00", "0"},
                {bsx::WeekDay::kSun, "00:00", "A"},
                {bsx::WeekDay::kMon, "00:00", "0"},
            },
            // counter
            "A",
            // expected
            {
                {cctz::weekday::monday,
                 {{sru::models::Daytime(12, 0), sru::models::Daytime(0, 0)}}},
                {cctz::weekday::wednesday,
                 {{sru::models::Daytime(12, 0), sru::models::Daytime(0, 0)}}},
                {cctz::weekday::sunday,
                 {{sru::models::Daytime(0, 0), sru::models::Daytime(0, 0)}}},
            },
        },

        BuildWeekdayScheduleForCounterParam{
            // schedule items
            {
                {bsx::WeekDay::kMon, "12:00", "A"},
                {bsx::WeekDay::kMon, "16:00", "B"},
                {bsx::WeekDay::kMon, "18:00", "0"},
            },
            // counter
            "A",
            // expected
            {
                {cctz::weekday::monday,
                 {{sru::models::Daytime(12, 0), sru::models::Daytime(16, 0)}}},
            },
        },

        BuildWeekdayScheduleForCounterParam{
            // schedule items
            {
                {bsx::WeekDay::kMon, "12:00", "A"},
                {bsx::WeekDay::kMon, "16:00", "B"},
                {bsx::WeekDay::kMon, "18:00", "0"},
            },
            // counter
            "B",
            // expected
            {
                {cctz::weekday::monday,
                 {{sru::models::Daytime(16, 0), sru::models::Daytime(18, 0)}}},
            },
        },

        BuildWeekdayScheduleForCounterParam{
            // schedule items
            {
                {bsx::WeekDay::kMon, "12:00", "A"},
                {bsx::WeekDay::kMon, "18:00", "0"},
            },
            // counter
            "B",
            // expected
            {},
        },

        BuildWeekdayScheduleForCounterParam{
            // schedule items
            {
                {bsx::WeekDay::kMon, "12:00", "A"},
                {bsx::WeekDay::kWed, "11:00", "0"},
                {bsx::WeekDay::kThu, "12:00", "B"},
                {bsx::WeekDay::kFri, "00:00", "A"},
                {bsx::WeekDay::kFri, "04:00", "B"},
                {bsx::WeekDay::kFri, "12:00", "A"},
                {bsx::WeekDay::kFri, "20:00", "0"},
            },
            // counter
            "A",
            // expected
            {
                {cctz::weekday::monday,
                 {{sru::models::Daytime(12, 0), sru::models::Daytime(0, 0)}}},
                {cctz::weekday::tuesday,
                 {{sru::models::Daytime(0, 0), sru::models::Daytime(0, 0)}}},
                {cctz::weekday::wednesday,
                 {{sru::models::Daytime(0, 0), sru::models::Daytime(11, 0)}}},
                {cctz::weekday::friday,
                 {{sru::models::Daytime(0, 0), sru::models::Daytime(4, 0)},
                  {sru::models::Daytime(12, 0), sru::models::Daytime(20, 0)}}},
            },
        },

        BuildWeekdayScheduleForCounterParam{
            // schedule items
            {
                {bsx::WeekDay::kMon, "12:00", "A"},
                {bsx::WeekDay::kWed, "11:00", "0"},
                {bsx::WeekDay::kThu, "12:00", "B"},
                {bsx::WeekDay::kFri, "00:00", "A"},
                {bsx::WeekDay::kFri, "04:00", "B"},
                {bsx::WeekDay::kFri, "12:00", "A"},
                {bsx::WeekDay::kFri, "20:00", "0"},
            },
            // counter
            "B",
            // expected
            {{cctz::weekday::thursday,
              {{sru::models::Daytime(12, 0), sru::models::Daytime(0, 0)}}},
             {cctz::weekday::friday,
              {{sru::models::Daytime(4, 0), sru::models::Daytime(12, 0)}}}},
        }

        ));

struct StripRangeToNonemptySchedule {
  sru::models::GoalWeekdaySchedule schedule_items;
  sru::models::LocalTimeRange local_range;
  sru::models::LocalTimeRange expected;
};

class StripRangeToNonemptyScheduleFixture
    : public testing::TestWithParam<StripRangeToNonemptySchedule> {};

TEST_P(StripRangeToNonemptyScheduleFixture, BuildsAsExpected) {
  const auto actual = sru::models::StripRangeToNonemptySchedule(
      GetParam().local_range, GetParam().schedule_items);
  EXPECT_EQ(GetParam().expected, actual);
}

INSTANTIATE_TEST_SUITE_P(
    GoalSchedule, StripRangeToNonemptyScheduleFixture,
    ::testing::Values(

        StripRangeToNonemptySchedule{
            // schedule items
            {
                {cctz::weekday::monday,
                 {{sru::models::Daytime(12, 0), sru::models::Daytime(0, 0)}}},
                {cctz::weekday::tuesday,
                 {{sru::models::Daytime(12, 0), sru::models::Daytime(0, 0)}}},
            },
            // local_range
            {
                cctz::civil_day(2020, 1, 6),  // mon
                cctz::civil_day(2020, 1, 10),
            },
            // expected
            {
                cctz::civil_day(2020, 1, 6),  // mon
                cctz::civil_day(2020, 1, 8),
            }},

        StripRangeToNonemptySchedule{
            // schedule items
            {
                {cctz::weekday::monday,
                 {{sru::models::Daytime(12, 0), sru::models::Daytime(0, 0)}}},
                {cctz::weekday::wednesday,
                 {{sru::models::Daytime(12, 0), sru::models::Daytime(0, 0)}}},
            },
            // local_range
            {
                cctz::civil_day(2020, 1, 4),   // sat
                cctz::civil_day(2020, 1, 11),  // sat
            },
            // expected
            {
                cctz::civil_day(2020, 1, 6),  // mon
                cctz::civil_day(2020, 1, 9),  // thu
            }},

        StripRangeToNonemptySchedule{
            // schedule items
            {
                {cctz::weekday::monday,
                 {{sru::models::Daytime(12, 0), sru::models::Daytime(0, 0)}}},
                {cctz::weekday::wednesday,
                 {{sru::models::Daytime(12, 0), sru::models::Daytime(0, 0)}}},
            },
            // local_range
            {
                cctz::civil_day(2020, 1, 6),  // mon
                cctz::civil_day(2020, 1, 9),  // thu
            },
            // expected
            {
                cctz::civil_day(2020, 1, 6),  // mon
                cctz::civil_day(2020, 1, 9),  // thu
            }},

        StripRangeToNonemptySchedule{
            // schedule items
            {
                {cctz::weekday::monday,
                 {{sru::models::Daytime(12, 0), sru::models::Daytime(0, 0)}}},
                {cctz::weekday::wednesday,
                 {{sru::models::Daytime(12, 0), sru::models::Daytime(0, 0)}}},
            },
            // local_range
            {
                cctz::civil_day(2020, 1, 4),   // sat
                cctz::civil_day(2020, 1, 25),  // sat
            },
            // expected
            {
                cctz::civil_day(2020, 1, 6),   // mon
                cctz::civil_day(2020, 1, 23),  // thu
            }},

        StripRangeToNonemptySchedule{
            // schedule items
            {
                {cctz::weekday::monday,
                 {{sru::models::Daytime(12, 0), sru::models::Daytime(0, 0)}}},
                {cctz::weekday::tuesday,
                 {{sru::models::Daytime(12, 0), sru::models::Daytime(0, 0)}}},
            },
            // local_range
            {
                cctz::civil_day(2020, 1, 4),  // sat
                cctz::civil_day(2020, 1, 5),  // sun
            },
            // expected
            {
                // (empty)
                cctz::civil_day(2020, 1, 5),
                cctz::civil_day(2020, 1, 5),
            }}

        ));

struct IsActiveData {
  sru::models::TimePoint time_point;
  bool expected;
};

struct IsActiveParametrized : public testing::TestWithParam<IsActiveData> {};

TEST_P(IsActiveParametrized, IsActiveParametrized) {
  const auto [time_point, expected] = GetParam();
  const sru::models::GoalWeekdaySchedule weekday_to_schedule{
      {cctz::weekday::monday, {{{0, 0}, {24, 0}}}},
      {cctz::weekday::wednesday, {{{10, 10}, {11, 11}}, {{12, 12}, {13, 13}}}},
      {cctz::weekday::sunday, {{{12, 0}, {24, 0}}}}};
  const sru::models::GoalSchedule schedule(
      ParseTime("2022-06-13T00:00:00+0000" /*monday*/),
      ParseTime("2022-06-20T00:00:00+0000"), cctz::utc_time_zone(), 7,
      weekday_to_schedule);
  EXPECT_EQ(schedule.IsActive(time_point), expected);
}

const std::vector<IsActiveData> kIsActiveData{
    {ParseTime("2022-06-12T00:00:00+0000"), false},  // before start
    {ParseTime("2022-06-13T12:00:00+0000"), true},   // mo
    {ParseTime("2022-06-14T12:00:00+0000"), false},  // tu
    {ParseTime("2022-06-15T09:00:00+0000"), false},  // wd
    {ParseTime("2022-06-15T10:30:00+0000"), true},   // wd
    {ParseTime("2022-06-15T11:30:00+0000"), false},  // wd
    {ParseTime("2022-06-15T12:30:00+0000"), true},   // wd
    {ParseTime("2022-06-15T13:30:00+0000"), false},  // wd
    {ParseTime("2022-06-17T12:00:00+0000"), false},  // fr
    {ParseTime("2022-06-19T03:00:00+0000"), false},  // su
    {ParseTime("2022-06-19T18:00:00+0000"), true},   // su
    {ParseTime("2022-06-20T00:00:00+0000"), false}   // after end
};

INSTANTIATE_TEST_SUITE_P(IsActiveParametrized, IsActiveParametrized,
                         ::testing::ValuesIn(kIsActiveData));

struct IsLastDayInWindowData {
  sru::models::TimePoint time_point;
  int window;
  bool expected;
};

struct IsLastDayInWindowParametrized
    : public testing::TestWithParam<IsLastDayInWindowData> {};

TEST_P(IsLastDayInWindowParametrized, IsLastDayInWindowParametrized) {
  const auto [time_point, window, expected] = GetParam();
  const sru::models::GoalWeekdaySchedule weekday_to_schedule{
      {cctz::weekday::monday, {{{0, 0}, {24, 0}}}}};
  const sru::models::GoalSchedule schedule(
      ParseTime("2022-06-13T00:00:00+0000"),
      ParseTime("2022-06-27T00:00:00+0000"), cctz::utc_time_zone(), window,
      weekday_to_schedule);
  EXPECT_EQ(schedule.IsLastDayInWindow(time_point), expected);
}

const std::vector<IsLastDayInWindowData> kIsLastDayInWindowData{
    {ParseTime("2022-06-12T23:59:59+0000"), 7, false},  // before start
    {ParseTime("2022-06-15T00:00:00+0000"), 7, false},  // not last day
    {ParseTime("2022-06-19T00:00:00+0000"), 7, true},   // last day
    {ParseTime("2022-06-19T12:00:00+0000"), 7, true},   // last day
    {ParseTime("2022-06-26T12:00:00+0000"), 7, true},   // last day
    {ParseTime("2022-06-27T00:00:01+0000"), 7, false},  // after end
    // window = 1 => all days in [begin, end) is last
    {ParseTime("2022-06-12T23:59:59+0000"), 1, false},  // before start
    {ParseTime("2022-06-15T00:00:00+0000"), 1, true},
    {ParseTime("2022-06-19T00:00:00+0000"), 1, true},
    {ParseTime("2022-06-19T12:00:00+0000"), 1, true},
    {ParseTime("2022-06-27T00:00:00+0000"), 1, false}};  // after end

INSTANTIATE_TEST_SUITE_P(IsLastDayInWindowParametrized,
                         IsLastDayInWindowParametrized,
                         ::testing::ValuesIn(kIsLastDayInWindowData));

struct GetScheduleForDayData {
  sru::models::TimePoint time_point;
  sru::models::GoalSchedule::EndedRangesPolicy policy;
  sru::models::ScheduleForDay expected_ranges;
  bool expected_in_last_daytime_range;
};

struct GetScheduleForDayParametrized
    : public testing::TestWithParam<GetScheduleForDayData> {};

TEST_P(GetScheduleForDayParametrized, GetScheduleForDayParametrized) {
  const auto [time_point, policy, expected_ranges,
              expected_in_last_daytime_range] = GetParam();
  const sru::models::GoalWeekdaySchedule weekday_to_schedule{
      {cctz::weekday::wednesday, {{{10, 10}, {11, 11}}, {{12, 12}, {13, 13}}}},
      {cctz::weekday::friday, {{{12, 0}, {24, 0}}}}};
  const sru::models::GoalSchedule schedule(
      ParseTime("2022-06-13T00:00:00+0000" /*monday*/),
      ParseTime("2022-06-20T00:00:00+0000"), cctz::utc_time_zone(), 7,
      weekday_to_schedule);
  const auto ranges = schedule.GetScheduleForDay(time_point, policy);
  EXPECT_EQ(ranges, expected_ranges);
  const auto in_last_daytime_range =
      schedule.IsTimePointInLastDaytimeRange(time_point);
  EXPECT_EQ(in_last_daytime_range, expected_in_last_daytime_range);
}

const std::vector<GetScheduleForDayData> kGetScheduleForDayData{
    // before start
    {ParseTime("2022-06-12T00:00:00+0000"),
     sru::models::GoalSchedule::EndedRangesPolicy::kInclude,
     {},
     false},
    {ParseTime("2022-06-12T00:00:00+0000"),
     sru::models::GoalSchedule::EndedRangesPolicy::kNotInclude,
     {},
     false},

    // wednesday
    {ParseTime("2022-06-15T03:00:00+0000"),
     sru::models::GoalSchedule::EndedRangesPolicy::kInclude,
     {{{10, 10}, {11, 11}}, {{12, 12}, {13, 13}}},
     false},
    {ParseTime("2022-06-15T03:00:00+0000"),
     sru::models::GoalSchedule::EndedRangesPolicy::kNotInclude,
     {{{10, 10}, {11, 11}}, {{12, 12}, {13, 13}}},
     false},
    {ParseTime("2022-06-15T10:30:00+0000"),
     sru::models::GoalSchedule::EndedRangesPolicy::kInclude,
     {{{10, 10}, {11, 11}}, {{12, 12}, {13, 13}}},
     false},
    {ParseTime("2022-06-15T10:30:00+0000"),
     sru::models::GoalSchedule::EndedRangesPolicy::kNotInclude,
     {{{10, 10}, {11, 11}}, {{12, 12}, {13, 13}}},
     false},
    {ParseTime("2022-06-15T11:30:00+0000"),
     sru::models::GoalSchedule::EndedRangesPolicy::kInclude,
     {{{10, 10}, {11, 11}}, {{12, 12}, {13, 13}}},
     false},
    {ParseTime("2022-06-15T11:30:00+0000"),
     sru::models::GoalSchedule::EndedRangesPolicy::kNotInclude,
     {{{12, 12}, {13, 13}}},
     false},
    {ParseTime("2022-06-15T12:30:00+0000"),
     sru::models::GoalSchedule::EndedRangesPolicy::kInclude,
     {{{10, 10}, {11, 11}}, {{12, 12}, {13, 13}}},
     true},
    {ParseTime("2022-06-15T12:30:00+0000"),
     sru::models::GoalSchedule::EndedRangesPolicy::kNotInclude,
     {{{12, 12}, {13, 13}}},
     true},
    {ParseTime("2022-06-15T13:30:00+0000"),
     sru::models::GoalSchedule::EndedRangesPolicy::kInclude,
     {{{10, 10}, {11, 11}}, {{12, 12}, {13, 13}}},
     false},
    {ParseTime("2022-06-15T13:30:00+0000"),
     sru::models::GoalSchedule::EndedRangesPolicy::kNotInclude,
     {},
     false},

    // thusday
    {ParseTime("2022-06-16T12:00:00+0000"),
     sru::models::GoalSchedule::EndedRangesPolicy::kInclude,
     {},
     false},
    {ParseTime("2022-06-16T12:00:00+0000"),
     sru::models::GoalSchedule::EndedRangesPolicy::kNotInclude,
     {},
     false},

    // friday
    {ParseTime("2022-06-17T01:00:00+0000"),
     sru::models::GoalSchedule::EndedRangesPolicy::kInclude,
     {{{12, 0}, {0, 0}}},
     false},
    {ParseTime("2022-06-17T01:00:00+0000"),
     sru::models::GoalSchedule::EndedRangesPolicy::kNotInclude,
     {{{12, 0}, {0, 0}}},
     false},
    {ParseTime("2022-06-17T13:00:00+0000"),
     sru::models::GoalSchedule::EndedRangesPolicy::kInclude,
     {{{12, 0}, {0, 0}}},
     true},
    {ParseTime("2022-06-17T13:00:00+0000"),
     sru::models::GoalSchedule::EndedRangesPolicy::kNotInclude,
     {{{12, 0}, {0, 0}}},
     true},

    // after end
    {ParseTime("2022-06-20T00:00:00+0000"),
     sru::models::GoalSchedule::EndedRangesPolicy::kInclude,
     {},
     false},
    {ParseTime("2022-06-20T00:00:00+0000"),
     sru::models::GoalSchedule::EndedRangesPolicy::kNotInclude,
     {},
     false},
};

INSTANTIATE_TEST_SUITE_P(GetScheduleForDayParametrized,
                         GetScheduleForDayParametrized,
                         ::testing::ValuesIn(kGetScheduleForDayData));

struct SameScheduleEveryWeekDayData {
  sru::models::GoalWeekdaySchedule weekday_to_schedule;
  bool is_same_schedule_expected;
  bool is_round_the_clock_schedule_expected;
};

struct SameScheduleEveryWeekDayParametrized
    : public testing::TestWithParam<SameScheduleEveryWeekDayData> {};
TEST_P(SameScheduleEveryWeekDayParametrized,
       SameScheduleEveryWeekDayParametrized) {
  const auto [weekday_to_schedule, is_same_schedule_expected,
              is_round_the_clock_schedule_expected] = GetParam();
  const sru::models::GoalSchedule schedule(
      ParseTime("2022-06-13T00:00:00+0000"),
      ParseTime("2022-06-20T00:00:00+0000"), cctz::utc_time_zone(), 7,
      weekday_to_schedule);
  EXPECT_EQ(schedule.IsSameScheduleEveryWeekDay(), is_same_schedule_expected);
  EXPECT_EQ(schedule.IsRoundTheClockScheduleEveryWeekDay(),
            is_round_the_clock_schedule_expected);
}

const std::vector<sru::models::DaytimeRange> kSomeDaySchedule{
    {{10, 10}, {11, 11}}, {{12, 12}, {13, 13}}};
const std::vector<sru::models::DaytimeRange> kRoundTheClockDaySchedule{
    {{0, 0}, {24, 0}}};
const std::vector<SameScheduleEveryWeekDayData> kSameScheduleEveryWeekDayData{
    // 1 day
    {{{cctz::weekday::monday, kSomeDaySchedule}}, false, false},
    // 6 days
    {{{cctz::weekday::monday, kSomeDaySchedule},
      {cctz::weekday::tuesday, kSomeDaySchedule},
      {cctz::weekday::wednesday, kSomeDaySchedule},
      {cctz::weekday::thursday, kSomeDaySchedule},
      {cctz::weekday::friday, kSomeDaySchedule},
      {cctz::weekday::saturday, kSomeDaySchedule}},
     false,
     false},
    // 7 days, not same
    {{{cctz::weekday::monday, kSomeDaySchedule},
      {cctz::weekday::tuesday, kSomeDaySchedule},
      {cctz::weekday::wednesday, kSomeDaySchedule},
      {cctz::weekday::thursday, kSomeDaySchedule},
      {cctz::weekday::friday, kSomeDaySchedule},
      {cctz::weekday::saturday, kSomeDaySchedule},
      {cctz::weekday::sunday, {{{10, 10}, {11, 11}}}}},
     false,
     false},
    // 7 days, same not empty
    {{{cctz::weekday::monday, kSomeDaySchedule},
      {cctz::weekday::tuesday, kSomeDaySchedule},
      {cctz::weekday::wednesday, kSomeDaySchedule},
      {cctz::weekday::thursday, kSomeDaySchedule},
      {cctz::weekday::friday, kSomeDaySchedule},
      {cctz::weekday::saturday, kSomeDaySchedule},
      {cctz::weekday::sunday, kSomeDaySchedule}},
     true,
     false},
    // 7 days, same not empty, 0-24
    {{{cctz::weekday::monday, kRoundTheClockDaySchedule},
      {cctz::weekday::tuesday, kRoundTheClockDaySchedule},
      {cctz::weekday::wednesday, kRoundTheClockDaySchedule},
      {cctz::weekday::thursday, kRoundTheClockDaySchedule},
      {cctz::weekday::friday, kRoundTheClockDaySchedule},
      {cctz::weekday::saturday, kRoundTheClockDaySchedule},
      {cctz::weekday::sunday, kRoundTheClockDaySchedule}},
     true,
     true}};

INSTANTIATE_TEST_SUITE_P(SameScheduleEveryWeekDayParametrized,
                         SameScheduleEveryWeekDayParametrized,
                         ::testing::ValuesIn(kSameScheduleEveryWeekDayData));

struct GetWindowData {
  sru::models::TimePoint time_point;
  sru::models::LocalTimeRange expected;
};

struct GetWindowParametrized : public testing::TestWithParam<GetWindowData> {};
TEST_P(GetWindowParametrized, GetWindowParametrized) {
  const auto [time_point, expected] = GetParam();
  const sru::models::GoalWeekdaySchedule weekday_to_schedule{
      {cctz::weekday::wednesday, {{{10, 10}, {11, 11}}, {{12, 12}, {13, 13}}}},
  };
  const sru::models::GoalSchedule schedule(
      ParseTime("2022-06-13T00:00:00+0000"),
      ParseTime("2022-06-27T00:00:00+0000"), cctz::utc_time_zone(), 7,
      weekday_to_schedule);
  EXPECT_EQ(schedule.GetCurrentOrNearestIncommingWindow(time_point), expected);
}

const sru::models::LocalTimeRange kFirstWindow{cctz::civil_second(2022, 6, 13),
                                               cctz::civil_second(2022, 6, 20)};
const sru::models::LocalTimeRange kLastWindow{cctz::civil_second(2022, 6, 20),
                                              cctz::civil_second(2022, 6, 27)};

const std::vector<GetWindowData> kGetWindowData{
    // before the start
    {ParseTime("2022-06-12T00:00:00+0000"), kFirstWindow},
    // start
    {ParseTime("2022-06-13T00:00:00+0000"), kFirstWindow},
    // middle of the first window
    {ParseTime("2022-06-15T00:00:00+0000"), kFirstWindow},
    // last day of the first window
    {ParseTime("2022-06-19T12:00:00+0000"), kFirstWindow},
    // middle of the last window
    {ParseTime("2022-06-22T00:00:00+0000"), kLastWindow}};
INSTANTIATE_TEST_SUITE_P(GetWindowParametrized, GetWindowParametrized,
                         ::testing::ValuesIn(kGetWindowData));
