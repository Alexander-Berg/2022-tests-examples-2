#include <gtest/gtest.h>

#include <string>
#include <unordered_set>
#include <utility>

#include <cctz/civil_time.h>

#include <userver/formats/json/string_builder.hpp>
#include <userver/utils/assert.hpp>
#include <userver/utils/datetime.hpp>
#include <userver/utils/mock_now.hpp>

#include <common_handlers/goals_summary/fetch_smart_goals.hpp>
#include <common_handlers/goals_summary/types.hpp>
#include <utils/time_range.hpp>
#include <utils/utils.hpp>
#include <views/driver/v1/subvention-view/v1/view/summary/get/types.hpp>

#include "mocked_bsx.hpp"

namespace dt = utils::datetime;

struct ByDriverRequestProcessingData {
  const utils::TimePoint requested_timepoint;
  const bsx::v2_by_driver::post::Response200 by_driver_response;
  const handlers::CounterToProgressMap expected_result;
};

struct ByDriverRequestProcessing
    : public ::testing::TestWithParam<ByDriverRequestProcessingData> {};

TEST_P(ByDriverRequestProcessing, Test) {
  mocks::BSXClient bsx_client;

  const auto& param = GetParam();

  formats::json::StringBuilder sb;
  bsx::v2_by_driver::post::WriteToStream(param.by_driver_response, sb);
  bsx_client.responses["V2ByDriver"].push_back(sb.GetString());

  const bool v2_by_driver_optimization = false;
  const auto function_result =
      GetProgressMap(handlers::MergedGoalsWithCounter({{}}), utils::TimeRange(),
                     param.requested_timepoint, "Europe/Moscow", "", bsx_client,
                     v2_by_driver_optimization);

  ASSERT_EQ(function_result, param.expected_result);
};

bsx::GoalPayoff MakeByDriverResponseElem(const std::string& counter,
                                         const int num_orders,
                                         const utils::TimeRange& range) {
  bsx::GoalPayoff payoff;
  payoff.counter = counter;
  payoff.num_orders = num_orders;
  payoff.period.start = range.from;
  payoff.period.end = range.to;
  return payoff;
}

INSTANTIATE_TEST_SUITE_P(
    ByDriverRequestProcessing, ByDriverRequestProcessing,
    ::testing::ValuesIn(
        {ByDriverRequestProcessingData{
             dt::Stringtime("2020-10-11T12:00:00Z"),
             bsx::v2_by_driver::post::Response200{bsx::V2ByDriverResponse{
                 {MakeByDriverResponseElem(
                      "c1", 1,
                      {dt::Stringtime("2020-10-10T12:00:00Z"),
                       dt::Stringtime("2020-10-12T12:00:00Z")}),
                  MakeByDriverResponseElem(
                      "c2", 2,
                      {dt::Stringtime("2020-10-10T12:00:00Z"),
                       dt::Stringtime("2020-10-11T12:00:00Z")}),
                  MakeByDriverResponseElem(
                      "c3", 3,
                      {dt::Stringtime("2020-10-11T12:00:00Z"),
                       dt::Stringtime("2020-10-12T12:00:00Z")}),
                  MakeByDriverResponseElem(
                      "c4", 4,
                      {dt::Stringtime("2020-10-09T12:00:00Z"),
                       dt::Stringtime("2020-10-10T12:00:00Z")}),
                  MakeByDriverResponseElem(
                      "c5", 5,
                      {dt::Stringtime("2020-10-12T12:00:00Z"),
                       dt::Stringtime("2020-10-13T12:00:00Z")})}}},
             {{"c1", 1}, {"c3", 3}}},
         ByDriverRequestProcessingData{
             dt::Stringtime("2020-10-11T12:00:00Z"),
             bsx::v2_by_driver::post::Response200{bsx::V2ByDriverResponse{{}}},
             {}}}));

struct ByDriverTimeRangePreparationData {
  const utils::TimePoint requested_timepoint;
  const utils::TimeRange expected_result;
};

struct ByDriverTimeRangePreparation
    : public ::testing::TestWithParam<ByDriverTimeRangePreparationData> {};

TEST_P(ByDriverTimeRangePreparation, Test) {
  dt::MockNowSet(dt::Stringtime("2020-10-11T12:00:00Z"));
  const auto& param = GetParam();
  const auto function_result = handlers::GetDayTimeRangeForProgressMap(
      param.requested_timepoint, "Europe/Moscow");
  ASSERT_EQ(function_result, param.expected_result);
};

INSTANTIATE_TEST_SUITE_P(
    ByDriverTimeRangePreparation, ByDriverTimeRangePreparation,
    ::testing::ValuesIn({ByDriverTimeRangePreparationData{
                             dt::Stringtime("2020-10-09T12:00:00Z"),
                             {dt::Stringtime("2020-10-08T21:00:00Z"),
                              dt::Stringtime("2020-10-11T21:00:00Z")}},
                         ByDriverTimeRangePreparationData{
                             dt::Stringtime("2020-10-11T12:00:00Z"),
                             {dt::Stringtime("2020-10-10T21:00:00Z"),
                              dt::Stringtime("2020-10-11T21:00:00Z")}},
                         ByDriverTimeRangePreparationData{
                             dt::Stringtime("2020-10-13T12:00:00Z"),
                             {dt::Stringtime("2020-10-12T21:00:00Z"),
                              dt::Stringtime("2020-10-13T21:00:00Z")}}}));

struct TestSortFunctionData {
  handlers::GoalWithProgress better_goal;
  handlers::GoalWithProgress worse_goal;
};

struct TestSortFunctionParametrized
    : public ::testing::TestWithParam<TestSortFunctionData> {};

TEST_P(TestSortFunctionParametrized, Test) {
  const auto [better_goal, worse_goal] = GetParam();
  const auto res = handlers::driver_v1_subvention_view_v1_view_summary::get::
      impl::GetShortestWayToMaxIncomeGoal({better_goal, worse_goal});
  ASSERT_EQ(res, better_goal);
}

handlers::GoalWithProgress MakeGoalWithProgressForSorting(
    const handlers::TimePoint end, const std::vector<handlers::GoalStep> steps,
    const size_t progress) {
  handlers::GoalWithProgress goal;
  goal.end = end;
  goal.goal_steps = steps;
  goal.progress = progress;
  return goal;
}

const std::vector<TestSortFunctionData> kTestSortFunctionData = {
    {MakeGoalWithProgressForSorting(dt::Stringtime("2021-12-27T12:00:00Z"), {},
                                    0),
     MakeGoalWithProgressForSorting(dt::Stringtime("2021-12-28T12:00:00Z"), {},
                                    0)},

    {MakeGoalWithProgressForSorting(dt::Stringtime("2021-12-27T12:00:00Z"),
                                    {{10, "100"}}, 5),
     MakeGoalWithProgressForSorting(dt::Stringtime("2021-12-27T12:00:00Z"),
                                    {{20, "100"}}, 5)},

    {MakeGoalWithProgressForSorting(dt::Stringtime("2021-12-27T12:00:00Z"),
                                    {{10, "100"}, {20, "300"}}, 15),
     MakeGoalWithProgressForSorting(dt::Stringtime("2021-12-27T12:00:00Z"),
                                    {{20, "100"}, {30, "200"}}, 25)}};

const auto kNow = dt::Stringtime("2021-12-27T12:00:00Z");
const auto kTimeZoneName = "UTC";

INSTANTIATE_TEST_SUITE_P(TestSortFunctionParametrized,
                         TestSortFunctionParametrized,
                         ::testing::ValuesIn(kTestSortFunctionData));

using SearchDirection = handlers::driver_v1_subvention_view_v1_view_summary::
    get::impl::SearchDirection;

struct TestGetGoalsFromNearestDayData {
  std::vector<handlers::GoalWithProgress> goals;
  SearchDirection direction;
  size_t expected_number_of_goals;
  cctz::civil_day expected_day;
};

struct TestGetNeareatGoalParametrized
    : ::testing::TestWithParam<TestGetGoalsFromNearestDayData> {};

TEST_P(TestGetNeareatGoalParametrized, Test) {
  dt::MockNowSet(kNow);
  auto [goals, direction, expected_number_of_goals, expected_day] = GetParam();
  const auto now = utils::datetime::Now();

  const auto [res_goals, res_day] =
      handlers::driver_v1_subvention_view_v1_view_summary::get::impl::
          GetNearestDayGoalsAndNumber(std::move(goals), now, kTimeZoneName,
                                      direction);

  std::unordered_multiset<std::string> goals_ids;
  for (const auto& goal : res_goals) {
    ASSERT_EQ(goal.rule_id.back(), '1');
    goals_ids.insert(goal.rule_id);
  }

  ASSERT_EQ(goals_ids.size(), expected_number_of_goals);
  ASSERT_EQ(res_day, expected_day);
}

handlers::GoalWithProgress MakeGoalWithProgressForNearest(
    const std::string rule_id, const handlers::GoalSchedule schedule) {
  handlers::GoalWithProgress goal;
  goal.rule_id = rule_id;
  goal.schedule = schedule;
  return goal;
}

static const auto kTimeZone = utils::MakeTimeZone(kTimeZoneName);
const auto kToday = cctz::civil_day(cctz::convert(kNow, kTimeZone));
const auto kTomorrow = kToday + 1;
const auto kAfterTommorow = kTomorrow + 1;
const auto kYesterday = kToday - 1;
const auto kBeforeYesterday = kYesterday - 1;

struct Ranges {
  std::string from;
  std::string to;
};

std::vector<handlers::ScheduleRange> MakeSchedule(
    const std::vector<Ranges>& ranges) {
  std::vector<handlers::ScheduleRange> result;
  const auto str_to_minute = [](const std::string& str) {
    return cctz::civil_minute(cctz::convert(dt::Stringtime(str), kTimeZone));
  };
  for (const auto& [from, to] : ranges) {
    result.push_back({str_to_minute(from), str_to_minute(to)});
  }
  return result;
}

const auto kTodayMorningRange =
    MakeSchedule({{"2021-12-27T05:00:00Z", "2021-12-27T08:00:00Z"}});
const auto kTodayEveningRange =
    MakeSchedule({{"2021-12-27T18:00:00Z", "2021-12-27T19:00:00Z"}});
const auto kTodayIntersectNow =
    MakeSchedule({{"2021-12-27T11:00:00Z", "2021-12-27T15:00:00Z"}});

const auto kTomorrowRange1 =
    MakeSchedule({{"2021-12-28T10:00:00Z", "2021-12-28T20:00:00Z"}});
const auto kTomorrowRange2 =
    MakeSchedule({{"2021-12-28T08:00:00Z", "2021-12-28T12:00:00Z"}});
const auto kYesterdayRange1 =
    MakeSchedule({{"2021-12-26T10:00:00Z", "2021-12-26T20:00:00Z"}});
const auto kYesterdayRange2 =
    MakeSchedule({{"2021-12-26T08:00:00Z", "2021-12-26T12:00:00Z"}});

const auto kAfterTomorrowRange1 =
    MakeSchedule({{"2021-12-29T10:00:00Z", "2021-12-29T20:00:00Z"}});
const auto kAfterTomorrowRange2 =
    MakeSchedule({{"2021-12-29T08:00:00Z", "2021-12-29T12:00:00Z"}});
const auto kBeforeYesterdayRange1 =
    MakeSchedule({{"2021-12-25T10:00:00Z", "2021-12-25T20:00:00Z"}});
const auto kBeforeYesterdayRange2 =
    MakeSchedule({{"2021-12-25T08:00:00Z", "2021-12-25T12:00:00Z"}});

const std::vector<TestGetGoalsFromNearestDayData>
    kTestGetGoalsFromNearestDayData = {
        {{MakeGoalWithProgressForNearest("today_1_0",
                                         {{kToday, {kTodayMorningRange}}}),
          MakeGoalWithProgressForNearest("today_2_1",
                                         {{kToday, {kTodayIntersectNow}}}),
          MakeGoalWithProgressForNearest("today_3_1",
                                         {{kToday, {kTodayIntersectNow}}}),
          MakeGoalWithProgressForNearest(
              "today_4_0",
              {{kToday, {kTodayMorningRange}}, {kTomorrow, {kTomorrowRange1}}}),
          MakeGoalWithProgressForNearest(
              "today_5_0", {{kToday, {kTodayMorningRange}},
                            {kAfterTommorow, {kAfterTomorrowRange1}}})},
         SearchDirection::kFromNowToFuture,
         2,
         kToday},
        {{MakeGoalWithProgressForNearest("today_1_0",
                                         {{kToday, {kTodayEveningRange}}}),
          MakeGoalWithProgressForNearest("today_2_1",
                                         {{kToday, {kTodayIntersectNow}}}),
          MakeGoalWithProgressForNearest("today_3_1",
                                         {{kToday, {kTodayIntersectNow}}}),
          MakeGoalWithProgressForNearest("today_4_0",
                                         {{kToday, {kTodayEveningRange}},
                                          {kYesterday, {kYesterdayRange1}}}),
          MakeGoalWithProgressForNearest(
              "today_5_0", {{kToday, {kTodayEveningRange}},
                            {kBeforeYesterday, {kBeforeYesterdayRange1}}})},
         SearchDirection::kFromNowToPast,
         2,
         kToday},
        {{MakeGoalWithProgressForNearest(
              "today_5_0", {{kToday, {kTodayMorningRange}},
                            {kAfterTommorow, {kAfterTomorrowRange1}}}),
          MakeGoalWithProgressForNearest("tomorrow_1_1",
                                         {{kTomorrow, {kTomorrowRange1}}}),
          MakeGoalWithProgressForNearest("tomorrow_2_1",
                                         {{kTomorrow, {kTomorrowRange2}}}),
          MakeGoalWithProgressForNearest(
              "after_tomorrow_1_0",
              {{kAfterTommorow, {kAfterTomorrowRange1}}})},
         SearchDirection::kFromNowToFuture,
         2,
         kTomorrow},
        {{MakeGoalWithProgressForNearest(
              "today_5_0", {{kToday, {kTodayEveningRange}},
                            {kBeforeYesterday, {kBeforeYesterdayRange1}}}),
          MakeGoalWithProgressForNearest("yesterday_1_1",
                                         {{kYesterday, {kYesterdayRange1}}}),
          MakeGoalWithProgressForNearest("yesterday_2_1",
                                         {{kYesterday, {kYesterdayRange2}}}),
          MakeGoalWithProgressForNearest(
              "before_yesterday_1_0",
              {{kBeforeYesterday, {kBeforeYesterdayRange1}}})},
         SearchDirection::kFromNowToPast,
         2,
         kYesterday},
        {{MakeGoalWithProgressForNearest("today_1_0",
                                         {{kToday, {kTodayMorningRange}}}),
          MakeGoalWithProgressForNearest(
              "after_tomorrow_1_1", {{kAfterTommorow, {kAfterTomorrowRange1}}}),
          MakeGoalWithProgressForNearest(
              "after_tomorrow_2_1",
              {{kAfterTommorow, {kAfterTomorrowRange2}}})},
         SearchDirection::kFromNowToFuture,
         2,
         kAfterTommorow},
        {{MakeGoalWithProgressForNearest("today_1_0",
                                         {{kToday, {kTodayEveningRange}}}),
          MakeGoalWithProgressForNearest(
              "before_yesterday_1_1",
              {{kBeforeYesterday, {kBeforeYesterdayRange1}}}),
          MakeGoalWithProgressForNearest(
              "before_yesterday_2_1",
              {{kBeforeYesterday, {kBeforeYesterdayRange2}}})},
         SearchDirection::kFromNowToPast,
         2,
         kBeforeYesterday}};

INSTANTIATE_TEST_SUITE_P(TestGetNeareatGoalParametrized,
                         TestGetNeareatGoalParametrized,
                         ::testing::ValuesIn(kTestGetGoalsFromNearestDayData));

struct TestGetGoalsBasedOnScheduleData {
  std::vector<handlers::GoalWithProgress> goals;
  SearchDirection direction;
  size_t expected_number_of_goals;
  cctz::civil_day nearest_day;
};

struct TestGetGoalsBasedOnScheduleParametrized
    : ::testing::TestWithParam<TestGetGoalsBasedOnScheduleData> {};

TEST_P(TestGetGoalsBasedOnScheduleParametrized, Test) {
  dt::MockNowSet(kNow);
  auto [goals, direction, expected_number_of_goals, nearest_day] = GetParam();
  const auto now = utils::datetime::Now();

  const auto res_goals = handlers::driver_v1_subvention_view_v1_view_summary::
      get::impl::GetGoalsBasedOnSchedule(std::move(goals), nearest_day, now,
                                         kTimeZoneName, direction);

  std::unordered_multiset<std::string> goals_ids;
  for (const auto& goal : res_goals) {
    ASSERT_EQ(goal.rule_id.back(), '1');
    goals_ids.insert(goal.rule_id);
  }

  ASSERT_EQ(goals_ids.size(), expected_number_of_goals);
}

const auto k1CaseTodayBetter =
    MakeSchedule({{"2021-12-27T13:00:00Z", "2021-12-27T14:00:00Z"},
                  {"2021-12-27T16:00:00Z", "2021-12-27T17:00:00Z"}});
const auto k1CaseTodayWorse =
    MakeSchedule({{"2021-12-27T15:00:00Z", "2021-12-27T17:00:00Z"},
                  {"2021-12-27T18:00:00Z", "2021-12-27T19:00:00Z"}});

const auto k6CaseTodayBetter =
    MakeSchedule({{"2021-12-27T10:00:00Z", "2021-12-27T11:00:00Z"},
                  {"2021-12-27T07:00:00Z", "2021-12-27T08:00:00Z"}});
const auto k6CaseTodayWorse =
    MakeSchedule({{"2021-12-27T07:00:00Z", "2021-12-27T09:00:00Z"},
                  {"2021-12-27T05:00:00Z", "2021-12-27T06:00:00Z"}});

const auto k2CaseTodayBetter =
    MakeSchedule({{"2021-12-27T10:00:00Z", "2021-12-27T14:00:00Z"}});
const auto k2CaseTodayWorse =
    MakeSchedule({{"2021-12-27T13:00:00Z", "2021-12-27T15:00:00Z"}});

const auto k7CaseTodayBetter =
    MakeSchedule({{"2021-12-27T10:00:00Z", "2021-12-27T14:00:00Z"}});
const auto k7CaseTodayWorse =
    MakeSchedule({{"2021-12-27T09:00:00Z", "2021-12-27T11:00:00Z"}});

const auto k3CaseTodayGood1 =
    MakeSchedule({{"2021-12-27T10:00:00Z", "2021-12-27T14:00:00Z"}});
const auto k3CaseTodayGood2 =
    MakeSchedule({{"2021-12-27T09:00:00Z", "2021-12-27T13:00:00Z"}});

const auto k8CaseTodayGood1 =
    MakeSchedule({{"2021-12-27T10:00:00Z", "2021-12-27T14:00:00Z"}});
const auto k8CaseTodayGood2 =
    MakeSchedule({{"2021-12-27T09:00:00Z", "2021-12-27T13:00:00Z"}});

const auto k4CaseTomorrowBetter =
    MakeSchedule({{"2021-12-28T10:00:00Z", "2021-12-28T12:00:00Z"}});
const auto k4CaseTommorowWorse =
    MakeSchedule({{"2021-12-28T11:00:00Z", "2021-12-28T15:00:00Z"}});

const auto k9CaseYesterdayBetter =
    MakeSchedule({{"2021-12-26T12:00:00Z", "2021-12-26T14:00:00Z"}});
const auto k9CaseYesterdayWorse =
    MakeSchedule({{"2021-12-26T09:00:00Z", "2021-12-26T13:00:00Z"}});

const auto k5CaseTomorкowGood1 =
    MakeSchedule({{"2021-12-28T10:00:00Z", "2021-12-28T12:00:00Z"}});
const auto k5CaseTomorrowGood2 =
    MakeSchedule({{"2021-12-28T10:00:00Z", "2021-12-28T18:00:00Z"}});

const auto k10CaseYesterdayGood1 =
    MakeSchedule({{"2021-12-28T12:00:00Z", "2021-12-28T14:00:00Z"}});
const auto k10CaseYesterdayGood2 =
    MakeSchedule({{"2021-12-28T06:00:00Z", "2021-12-28T14:00:00Z"}});

const std::vector<TestGetGoalsBasedOnScheduleData>
    kTestGetGoalsBasedOnScheduleData = {
        {{MakeGoalWithProgressForNearest("today_1_0",
                                         {{kToday, {k1CaseTodayWorse}}}),
          MakeGoalWithProgressForNearest("today_2_1",
                                         {{kToday, {k1CaseTodayBetter}}})},
         SearchDirection::kFromNowToFuture,
         1,
         kToday},
        {{MakeGoalWithProgressForNearest("today_3_0",
                                         {{kToday, {k2CaseTodayWorse}}}),
          MakeGoalWithProgressForNearest("today_4_1",
                                         {{kToday, {k2CaseTodayBetter}}})},
         SearchDirection::kFromNowToFuture,
         1,
         kToday},
        {{MakeGoalWithProgressForNearest("today_5_1",
                                         {{kToday, {k3CaseTodayGood1}}}),
          MakeGoalWithProgressForNearest("today_6_1",
                                         {{kToday, {k3CaseTodayGood1}}})},
         SearchDirection::kFromNowToFuture,
         2,
         kToday},
        {{MakeGoalWithProgressForNearest("tomorrow_1_0",
                                         {{kTomorrow, {k4CaseTommorowWorse}}}),
          MakeGoalWithProgressForNearest(
              "tomorrow_2_1", {{kTomorrow, {k4CaseTomorrowBetter}}})},
         SearchDirection::kFromNowToFuture,
         1,
         kTomorrow},
        {{MakeGoalWithProgressForNearest("tomorrow_3_1",
                                         {{kTomorrow, {k5CaseTomorкowGood1}}}),
          MakeGoalWithProgressForNearest("tomorrow_4_1",
                                         {{kTomorrow, {k5CaseTomorrowGood2}}})},
         SearchDirection::kFromNowToFuture,
         2,
         kTomorrow},
        {{MakeGoalWithProgressForNearest("today_1_0",
                                         {{kToday, {k6CaseTodayWorse}}}),
          MakeGoalWithProgressForNearest("today_2_1",
                                         {{kToday, {k6CaseTodayBetter}}})},
         SearchDirection::kFromNowToPast,
         1,
         kToday},
        {{MakeGoalWithProgressForNearest("today_3_0",
                                         {{kToday, {k7CaseTodayWorse}}}),
          MakeGoalWithProgressForNearest("today_4_1",
                                         {{kToday, {k7CaseTodayBetter}}})},
         SearchDirection::kFromNowToPast,
         1,
         kToday},
        {{MakeGoalWithProgressForNearest("today_5_1",
                                         {{kToday, {k8CaseTodayGood1}}}),
          MakeGoalWithProgressForNearest("today_6_1",
                                         {{kToday, {k8CaseTodayGood1}}})},
         SearchDirection::kFromNowToPast,
         2,
         kToday},
        {{MakeGoalWithProgressForNearest(
              "yesterday_1_0", {{kYesterday, {k9CaseYesterdayWorse}}}),
          MakeGoalWithProgressForNearest(
              "yesterday_2_1", {{kYesterday, {k9CaseYesterdayBetter}}})},
         SearchDirection::kFromNowToPast,
         1,
         kYesterday},
        {{MakeGoalWithProgressForNearest(
              "yesterday_3_1", {{kYesterday, {k10CaseYesterdayGood1}}}),
          MakeGoalWithProgressForNearest(
              "yesterday_4_1", {{kYesterday, {k10CaseYesterdayGood2}}})},
         SearchDirection::kFromNowToPast,
         2,
         kYesterday}};

INSTANTIATE_TEST_SUITE_P(TestGetGoalsBasedOnScheduleParametrized,
                         TestGetGoalsBasedOnScheduleParametrized,
                         ::testing::ValuesIn(kTestGetGoalsBasedOnScheduleData));

struct TestGetFunctionForIterationsData {
  std::vector<handlers::GoalWithProgress> goals;
  SearchDirection direction;
  cctz::civil_day expected_bound_day;
};

struct TestGetFunctionForIterationsParametrized
    : ::testing::TestWithParam<TestGetFunctionForIterationsData> {};

TEST_P(TestGetFunctionForIterationsParametrized, Test) {
  dt::MockNowSet(kNow);
  auto [goals, direction, expected_bound_day] = GetParam();

  const auto [check_condition, change_counter] =
      handlers::driver_v1_subvention_view_v1_view_summary::get::impl::
          GetFunctionsForIterations(std::move(goals), direction);

  ASSERT_TRUE(check_condition(expected_bound_day));
  cctz::civil_day next_iter_day(expected_bound_day);
  change_counter(next_iter_day);
  ASSERT_FALSE(check_condition(next_iter_day));
  if (direction == SearchDirection::kFromNowToFuture) {
    ASSERT_EQ(expected_bound_day, next_iter_day - 1);
  } else {
    ASSERT_EQ(expected_bound_day, next_iter_day + 1);
  }
}

const std::vector<TestGetFunctionForIterationsData>
    kTestGetFunctionForIterationsData = {
        {{MakeGoalWithProgressForNearest("tomorrow",
                                         {{kTomorrow, {kTomorrowRange1}}})},
         SearchDirection::kFromNowToFuture,
         kTomorrow},
        {{MakeGoalWithProgressForNearest("yesterday",
                                         {{kYesterday, {kYesterdayRange1}}})},
         SearchDirection::kFromNowToPast,
         kYesterday},
        {{MakeGoalWithProgressForNearest(
             "after_tomorrow", {{kTomorrow, {kTomorrowRange1}},
                                {kAfterTommorow, {kAfterTomorrowRange1}}})},
         SearchDirection::kFromNowToFuture,
         kAfterTommorow},
        {{MakeGoalWithProgressForNearest(
             "before_yesterday",
             {{kYesterday, {kYesterdayRange1}},
              {kBeforeYesterday, {kBeforeYesterdayRange1}}})},
         SearchDirection::kFromNowToPast,
         kBeforeYesterday},
        {{
             MakeGoalWithProgressForNearest("tomorrow1",
                                            {{kTomorrow, {kTomorrowRange1}}}),
             MakeGoalWithProgressForNearest("tomorrow2",
                                            {{kTomorrow, {kTomorrowRange2}}}),
             MakeGoalWithProgressForNearest(
                 "after_tomorrow1", {{kTomorrow, {kTomorrowRange1}},
                                     {kAfterTommorow, {kAfterTomorrowRange1}}}),
             MakeGoalWithProgressForNearest(
                 "after_tomorrow2", {{kAfterTommorow, {kAfterTomorrowRange2}}}),
         },
         SearchDirection::kFromNowToFuture,
         kAfterTommorow},
        {{MakeGoalWithProgressForNearest("yesterday1",
                                         {{kYesterday, {kYesterdayRange1}}}),
          MakeGoalWithProgressForNearest("yesterday2",
                                         {{kYesterday, {kYesterdayRange2}}}),
          MakeGoalWithProgressForNearest(
              "before_yesterday1",
              {{kYesterday, {kYesterdayRange1}},
               {kBeforeYesterday, {kBeforeYesterdayRange1}}}),
          MakeGoalWithProgressForNearest(
              "before_yesterday2",
              {{kBeforeYesterday, {kBeforeYesterdayRange2}}})},

         SearchDirection::kFromNowToPast,
         kBeforeYesterday},
};

INSTANTIATE_TEST_SUITE_P(
    TestGetFunctionForIterationsParametrized,
    TestGetFunctionForIterationsParametrized,
    ::testing::ValuesIn(kTestGetFunctionForIterationsData));
