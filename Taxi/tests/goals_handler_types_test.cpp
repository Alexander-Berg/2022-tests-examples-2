#include <gtest/gtest.h>

#include <clients/billing-subventions-x/definitions.hpp>

#include <cstddef>
#include <random>

#include <testing/taxi_config.hpp>
#include <userver/utils/datetime.hpp>
#include <userver/utils/mock_now.hpp>

#include <common_handlers/goals_summary/fetch_smart_goals.hpp>
#include <common_handlers/goals_summary/requirements.hpp>
#include <common_handlers/goals_summary/types.hpp>
#include <helpers/schedule.hpp>
#include <utils/utils.hpp>

namespace bsx = clients::billing_subventions_x;
namespace dt = utils::datetime;

using TimeRange = utils::TimeRange;

namespace handlers {

bool operator==(const GoalWithCounter& lhs, const GoalWithCounter& rhs) {
  return std::tie(lhs.steps, lhs.rule, lhs.counter) ==
         std::tie(rhs.steps, rhs.rule, rhs.counter);
}

bool operator==(const TimeRange& lhs, const TimeRange& rhs) {
  return lhs.from == rhs.from && lhs.to == rhs.to;
}

}  // namespace handlers

namespace tests {

std::vector<bsx::GoalScheduleItem> CreateScheduleA() {
  std::vector<bsx::GoalScheduleItem> res;
  res.push_back({bsx::WeekDay::kMon, "17:15", "counter1"});
  res.push_back({bsx::WeekDay::kMon, "18:15", "0"});
  res.push_back({bsx::WeekDay::kMon, "19:15", "counter1"});
  res.push_back({bsx::WeekDay::kTue, "12:00", "counter2"});
  res.push_back({bsx::WeekDay::kWed, "11:00", "0"});
  res.push_back({bsx::WeekDay::kThu, "13:00", "counter1"});
  res.push_back({bsx::WeekDay::kSun, "18:00", "counter2"});
  return res;
}

std::vector<bsx::GoalStep> kCounter1Steps = {{10, "100"}, {20, "150"}};
std::vector<bsx::GoalStep> kCounter2Steps = {{5, "20"}, {7, "30"}};

std::vector<bsx::GoalCounterSteps> CreateStepsA() {
  std::vector<bsx::GoalCounterSteps> res;
  res.push_back({"counter1", kCounter1Steps});
  res.push_back({"counter2", kCounter2Steps});
  return res;
}

std::vector<bsx::CountersMapping> CreateCounterMappingA() {
  return {
      {"counter1", "global_counter1"},
      {"counter2", "global_counter2"},
  };
}

bsx::GoalRule CreateRuleA() {
  bsx::GoalRule res;
  res.draft_id = "draft_id_a";
  res.counters.schedule = CreateScheduleA();
  res.counters.steps = CreateStepsA();
  res.global_counters = CreateCounterMappingA();
  return res;
}

std::vector<bsx::GoalScheduleItem> CreateScheduleB() {
  std::vector<bsx::GoalScheduleItem> res;
  res.push_back({bsx::WeekDay::kWed, "11:00", "counter3"});
  res.push_back({bsx::WeekDay::kSun, "13:00", "0"});
  return res;
}

std::vector<bsx::GoalStep> kCounter3Steps = {{1, "500"}, {2, "1000"}};

std::vector<bsx::GoalCounterSteps> CreateStepsB() {
  std::vector<bsx::GoalCounterSteps> res;
  res.push_back({"counter3", kCounter3Steps});
  return res;
}

std::vector<bsx::CountersMapping> CreateCounterMappingB() {
  return {
      {"counter3", "global_counter3"},
  };
}

bsx::GoalRule CreateRuleB() {
  bsx::GoalRule res;
  res.draft_id = "draft_id_b";
  res.counters.schedule = CreateScheduleB();
  res.counters.steps = CreateStepsB();
  res.global_counters = CreateCounterMappingB();
  return res;
}

using GoalSchedule = std::vector<TimeRange>;

GoalSchedule kScheduleCounter1 = {{
                                      dt::Stringtime("2021-03-15T17:15:00Z"),
                                      dt::Stringtime("2021-03-15T18:15:00Z"),
                                  },
                                  {
                                      dt::Stringtime("2021-03-15T19:15:00Z"),
                                      dt::Stringtime("2021-03-16T12:00:00Z"),
                                  },
                                  {
                                      dt::Stringtime("2021-03-18T13:00:00Z"),
                                      dt::Stringtime("2021-03-21T18:00:00Z"),
                                  }};

GoalSchedule kScheduleCounter2 = {
    {
        dt::Stringtime("2021-03-15T00:00:00Z"),
        dt::Stringtime("2021-03-15T17:15:00Z"),
    },
    {
        dt::Stringtime("2021-03-16T12:00:00Z"),
        dt::Stringtime("2021-03-17T11:00:00Z"),
    },
    {
        dt::Stringtime("2021-03-21T18:00:00Z"),
        dt::Stringtime("2021-03-22T00:00:00Z"),
    },
};

GoalSchedule kScheduleCounter3 = {{
    dt::Stringtime("2021-03-17T11:00:00Z"),
    dt::Stringtime("2021-03-21T13:00:00Z"),
}};

struct ToGoalsTestData {
  bsx::GoalRule rule;
  handlers::GoalsWithCounter expected;
};

struct ToGoalsTestDataParametrized
    : public ::testing::TestWithParam<ToGoalsTestData> {};

TEST_P(ToGoalsTestDataParametrized, Variants) {
  const auto param = GetParam();
  const TimeRange kTimeRange = {
      dt::Stringtime("2021-03-15T00:00:00Z"),
      dt::Stringtime("2021-03-22T00:00:00Z"),
  };
  auto goals_with_counter = handlers::ToGoalWithCounter(
      param.rule, kTimeRange,
      {utils::MakeTimeZone("UTC"), utils::MakeTimeZone("UTC")}, {});
  sort(begin(goals_with_counter), end(goals_with_counter),
       [](const auto& lhs, const auto& rhs) {
         return lhs.counter < rhs.counter;
       });
  EXPECT_EQ(goals_with_counter, param.expected);
}

const std::vector<ToGoalsTestData> kToGoalsData{
    {CreateRuleA(),
     {{CreateRuleA(), kCounter1Steps, "global_counter1", false, std::nullopt},
      {CreateRuleA(), kCounter2Steps, "global_counter2", false, std::nullopt}}},
    {CreateRuleB(),
     {{CreateRuleB(), kCounter3Steps, "global_counter3", false,
       std::nullopt}}}};

INSTANTIATE_TEST_SUITE_P(GoalsTypes, ToGoalsTestDataParametrized,
                         ::testing::ValuesIn(kToGoalsData));

struct TestFilterData {
  TimeRange time_range;
  bool filtered;
};

struct TestFilterDataParametrized
    : public ::testing::TestWithParam<TestFilterData> {};

struct TestWindowData {
  int window_size = -1;
  TimeRange expected;
};

struct TestWindowParametrized
    : public ::testing::TestWithParam<TestWindowData> {};

TEST_P(TestWindowParametrized, Variants) {
  const auto param = GetParam();
  const auto window = handlers::GetWindow(
      dt::Stringtime("2021-01-08T00:00:00Z"), param.window_size,
      dt::Stringtime("2021-03-08T00:00:00Z"), cctz::utc_time_zone());
  EXPECT_EQ(window, param.expected);
}

const std::vector<TestWindowData> kTestWindowData = {
    {1,
     {dt::Stringtime("2021-03-08T00:00:00Z"),
      dt::Stringtime("2021-03-09T00:00:00Z")}},
    {2,
     {dt::Stringtime("2021-03-07T00:00:00Z"),
      dt::Stringtime("2021-03-09T00:00:00Z")}},
    {3,
     {dt::Stringtime("2021-03-06T00:00:00Z"),
      dt::Stringtime("2021-03-09T00:00:00Z")}},
    {10,
     {dt::Stringtime("2021-02-27T00:00:00Z"),
      dt::Stringtime("2021-03-09T00:00:00Z")}},
    {15,
     {dt::Stringtime("2021-02-22T00:00:00Z"),
      dt::Stringtime("2021-03-09T00:00:00Z")}},
    {30,
     {dt::Stringtime("2021-02-07T00:00:00Z"),
      dt::Stringtime("2021-03-09T00:00:00Z")}}};

INSTANTIATE_TEST_SUITE_P(GoalsTypes, TestWindowParametrized,
                         ::testing::ValuesIn(kTestWindowData));

struct TestGetWindowRespectsTimezoneData {
  utils::TimePoint rule_begin;
  utils::TimePoint ref_time;
  TimeRange expected;
};

struct TestGetWindowRespectsTimezone
    : public ::testing::TestWithParam<TestGetWindowRespectsTimezoneData> {};

TEST_P(TestGetWindowRespectsTimezone, Variants) {
  cctz::time_zone tz;
  cctz::load_time_zone("Europe/Tallinn", &tz);

  const auto window =
      handlers::GetWindow(dt::Stringtime("2021-10-29T21:00:00+0000"), 3,
                          dt::Stringtime("2021-10-29T21:00:00+0000"), tz);
  const TimeRange expected{dt::Stringtime("2021-10-29T21:00:00+0000"),
                           dt::Stringtime("2021-11-01T22:00:00+0000")};
  EXPECT_EQ(window, expected);
}

const std::vector<TestGetWindowRespectsTimezoneData>
    kTestGetWindowRespectsTimezoneData = {

        // Tallinn has change to winter time on October 31 2021

        // (window at the switch moment)
        {dt::Stringtime("2021-10-29T21:00:00+0000"),
         dt::Stringtime("2021-10-29T21:00:00+0000"),
         {dt::Stringtime("2021-10-29T21:00:00+0000"),
          dt::Stringtime("2021-11-01T22:00:00+0000")}},

        // (window after the switch moment)
        {dt::Stringtime("2021-10-29T21:00:00+0000"),
         dt::Stringtime("2021-11-01T21:00:00+0000"),
         {dt::Stringtime("2021-11-01T22:00:00+0000"),
          dt::Stringtime("2021-11-03T22:00:00+0000")}},

        // and change back to summer time on March 27 2022

        // (window at the switch moment)
        {dt::Stringtime("2022-03-25T22:00:00+0000"),
         dt::Stringtime("2022-03-25T22:00:00+0000"),
         {dt::Stringtime("2022-03-25T22:00:00+0000"),
          dt::Stringtime("2022-03-28T21:00:00+0000")}},

        // (window after the switch moment)
        {dt::Stringtime("2022-03-25T22:00:00+0000"),
         dt::Stringtime("2022-03-29T12:00:00+0000"),
         {dt::Stringtime("2022-03-28T21:00:00+0000"),
          dt::Stringtime("2022-03-31T21:00:00+0000")}}

};

INSTANTIATE_TEST_SUITE_P(
    GoalsTypes, TestGetWindowRespectsTimezone,
    ::testing::ValuesIn(kTestGetWindowRespectsTimezoneData));

TEST(GoalsTypes, Temporary) {
  cctz::time_zone tz;
  cctz::load_time_zone("Europe/Tallinn", &tz);

  const auto window =
      handlers::GetWindow(dt::Stringtime("2021-10-30T21:00:00+0000"), 1,
                          dt::Stringtime("2021-10-31T16:25:00+0000"), tz);
  const std::string expected =
      "<2021-10-30T21:00:00+0000; 2021-10-31T22:00:00+0000>";
  EXPECT_EQ(window.ToString(), expected);
}

struct TestSortRulesData {
  handlers::GoalsWithProgress goals;
  handlers::DriverInfo driver_info;
  std::vector<std::string> expected_counters;
};

struct TestSortRulesParametrized
    : public ::testing::TestWithParam<TestSortRulesData> {};

std::vector<std::string> GetGoalsCounters(
    const handlers::GoalsWithProgress& goals) {
  std::vector<std::string> res;
  for (const auto& goal : goals) {
    res.push_back(goal.counter.value_or("WTF?NO_COUNTER"));
  }
  return res;
}

class RequirementStrategyMock final : public handlers::RequirementStrategyBase {
 private:
  handlers::RequirementStatus CheckActivity(
      const handlers::GoalWithProgress& goal) const override {
    if (driver_info_.activity >= *goal.activity) {
      return handlers::RequirementStatus::kSatisfied;
    } else {
      return handlers::RequirementStatus::kViolated;
    }
  }
  handlers::RequirementStatus CheckBranding(
      const handlers::GoalWithProgress& /*goal*/) const override {
    return handlers::RequirementStatus::kSatisfied;
  }
  handlers::RequirementStatus CheckLocation(
      const handlers::GoalWithProgress& /*goal*/) const override {
    return handlers::RequirementStatus::kSatisfied;
  }
  handlers::RequirementStatus CheckTariff(
      const handlers::GoalWithProgress& /*goal*/) const override {
    return handlers::RequirementStatus::kSatisfied;
  }

 public:
  explicit RequirementStrategyMock(const handlers::DriverInfo driver_info)
      : driver_info_(driver_info) {}

  bool HasObstaclesToCompleteGoal(
      const handlers::GoalWithProgress& goal) const override {
    return !goal.IsCompleted() && !CheckAllRequirements(goal);
  }

 private:
  const handlers::DriverInfo driver_info_;
};

TEST_P(TestSortRulesParametrized, Variants) {
  auto [goals, driver_info, expected_counters] = GetParam();
  handlers::SortGoals(goals, RequirementStrategyMock(driver_info));
  EXPECT_EQ(GetGoalsCounters(goals), expected_counters);
}

handlers::DriverInfo MakeDriverInfo() {
  handlers::DriverInfo res;
  res.activity = 90;
  return res;
}

handlers::GoalWithProgress MakeGoalWithProgress(
    size_t progress, int window, size_t activity,
    const handlers::GoalSteps& goal_steps, std::string_view counter) {
  handlers::GoalWithProgress res;
  res.progress = progress;
  res.window = window;
  res.activity = activity;
  res.goal_steps = goal_steps;
  res.counter = counter;
  return res;
}

handlers::GoalsWithProgress MakeGoals() {
  using namespace handlers;
  GoalsWithProgress res;

  /// 3 with progress but not completed (2 with the same window size, one with
  /// different)
  res.push_back(
      MakeGoalWithProgress(2, 5, 30, GoalSteps{{4, "25"}, {7, "40"}}, "1"));
  res.push_back(MakeGoalWithProgress(1, 5, 30, GoalSteps{{5, "30"}}, "2"));
  res.push_back(MakeGoalWithProgress(1, 7, 30, GoalSteps{{5, "300"}}, "3"));

  /// 2 with 0 progress and satisfied restrictions
  res.push_back(MakeGoalWithProgress(0, 2, 80, GoalSteps{{7, "40"}}, "4"));
  res.push_back(MakeGoalWithProgress(0, 5, 85, GoalSteps{{5, "30"}}, "5"));

  /// 1 with 0 progress and not satisfied restrictions
  res.push_back(MakeGoalWithProgress(0, 1, 95, GoalSteps{{7, "40"}}, "6"));

  /// 2 completed
  res.push_back(MakeGoalWithProgress(7, 2, 30, GoalSteps{{4, "40"}}, "7"));
  res.push_back(MakeGoalWithProgress(5, 2, 30, GoalSteps{{5, "30"}}, "8"));

  /// make random shuffle
  std::random_device rd;
  std::mt19937 g(rd());
  std::shuffle(res.begin(), res.end(), g);

  return res;
}

static const std::vector<std::string> kExpectedCounters = {"1", "2", "3", "4",
                                                           "5", "6", "7", "8"};

const std::vector<TestSortRulesData> kTestSortRulesData = {
    {{}, MakeDriverInfo(), {}},
    {MakeGoals(), MakeDriverInfo(), kExpectedCounters}};

INSTANTIATE_TEST_SUITE_P(GoalsTypes, TestSortRulesParametrized,
                         ::testing::ValuesIn(kTestSortRulesData));

struct TestScheduleData {
  utils::TimeRange time_range;
  helpers::CounterToScheduleMap schedule;
};

struct TestScheduleParametrized
    : public ::testing::TestWithParam<TestScheduleData> {};

TEST_P(TestScheduleParametrized, Variants) {
  ::utils::datetime::MockNowSet(dt::Stringtime("2021-05-19T16:30:00Z"));

  const auto param = GetParam();
  static const std::vector<bsx::GoalScheduleItem> counters = {
      {bsx::WeekDay::kWed, "17:00", "A"},
      {bsx::WeekDay::kWed, "21:00", "0"},
  };
  const auto rule_time_zone = utils::MakeTimeZone("Europe/Moscow");
  const auto client_time_zone = utils::MakeTimeZone("Asia/Yekaterinburg");
  const auto schedule = helpers::GetSchedule(param.time_range, counters,
                                             rule_time_zone, client_time_zone);
  EXPECT_EQ(schedule, param.schedule);
}

const utils::TimeRange kTimeRangeInsideSchedule = {
    dt::Stringtime("2021-05-19T16:30:00Z"),
    dt::Stringtime("2021-05-19T16:33:00Z")};

const utils::TimeRange kTimeRangeIntersectsWithSchedule = {
    dt::Stringtime("2021-05-19T17:59:00Z"),
    dt::Stringtime("2021-05-19T18:01:00Z")};

const utils::TimeRange kTimeRangeAfterSchedule = {
    dt::Stringtime("2021-05-19T18:01:00Z"),
    dt::Stringtime("2021-05-19T18:04:00Z")};

const utils::TimeRange kTimeRangeBeforeSchedule = {
    dt::Stringtime("2021-05-19T13:57:00Z"),
    dt::Stringtime("2021-05-19T13:59:00Z")};

const std::vector<TestScheduleData> kTestScheduleData = {
    {kTimeRangeInsideSchedule, {{"A", {kTimeRangeInsideSchedule}}}},
    {kTimeRangeAfterSchedule, {}},
    {kTimeRangeBeforeSchedule, {}},
    {kTimeRangeIntersectsWithSchedule,
     {{"A",
       {{dt::Stringtime("2021-05-19T17:59:00Z"),
         dt::Stringtime("2021-05-19T18:00:00Z")}}}}}};

INSTANTIATE_TEST_SUITE_P(GoalsTypes, TestScheduleParametrized,
                         ::testing::ValuesIn(kTestScheduleData));

}  // namespace tests
