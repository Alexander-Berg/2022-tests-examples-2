#include <userver/utest/utest.hpp>

#include <common/smart_goals.hpp>

namespace cbsx = clients::billing_subventions_x;

namespace tests {

namespace {
const std::string kCounter = "some_local_counter";

cbsx::GoalRule CreateRule(std::vector<cbsx::GoalScheduleItem> sch) {
  cbsx::GoalRule rule;
  rule.counters.schedule = std::move(sch);
  rule.counters.steps = {
      cbsx::GoalCounterSteps{
          kCounter,
          {
              cbsx::GoalStep{
                  10,
                  "100",
              },
              cbsx::GoalStep{
                  20,
                  "200",
              },
          },
      },
  };
  return rule;
}

models::DoXGetYStepBarsForWeek CreateStepBars(
    const std::set<cbsx::WeekDay>& weekdays) {
  models::DoXGetYStepBarsForWeek result;
  for (auto weekday : weekdays) {
    result.at(static_cast<size_t>(weekday)) = models::DoXGetYStepBar{
        models::DoXGetYStep{
            10,
            11,
            100.0,
        },
        models::DoXGetYStep{
            20,
            std::nullopt,
            200.0,
        },
    };
  }
  return result;
}
}  // namespace

struct TestGetStepBarsParams {
  cbsx::GoalRule input_rule;
  models::DoXGetYStepBarsForWeek expected_result;
};

class TestGetStepBars
    : public testing::Test,
      public testing::WithParamInterface<TestGetStepBarsParams> {};

TEST_P(TestGetStepBars, Test) {
  const auto& p = GetParam();

  const auto result =
      common::smart_goals::GetDoXGetYStepBarsForWeek(std::vector{p.input_rule});
  ASSERT_EQ(p.expected_result, result);
}

INSTANTIATE_TEST_SUITE_P(
    GetStepBars, TestGetStepBars,
    testing::Values(
        // No schedule
        // => empty step bars
        TestGetStepBarsParams{
            CreateRule({}),
            CreateStepBars({}),
        },
        // Enabled one day with start and end in one day
        // => that day in step bars
        TestGetStepBarsParams{
            CreateRule({
                cbsx::GoalScheduleItem{
                    cbsx::WeekDay::kWed,
                    "00:00",
                    kCounter,
                },
                cbsx::GoalScheduleItem{
                    cbsx::WeekDay::kWed,
                    "23:59",
                    "0",
                },
            }),
            CreateStepBars({
                cbsx::WeekDay::kWed,
            }),
        },
        // Enabled one day with end in next day
        // => next day is not in step bars
        TestGetStepBarsParams{
            CreateRule({
                cbsx::GoalScheduleItem{
                    cbsx::WeekDay::kWed,
                    "00:00",
                    kCounter,
                },
                cbsx::GoalScheduleItem{
                    cbsx::WeekDay::kThu,
                    "00:00",
                    "0",
                },
            }),
            CreateStepBars({
                cbsx::WeekDay::kWed,
            }),
        },
        // Days range enabled
        // => that range is in step bars
        TestGetStepBarsParams{
            CreateRule({
                cbsx::GoalScheduleItem{
                    cbsx::WeekDay::kTue,
                    "00:00",
                    kCounter,
                },
                cbsx::GoalScheduleItem{
                    cbsx::WeekDay::kFri,
                    "00:01",
                    "0",
                },
            }),
            CreateStepBars({
                cbsx::WeekDay::kTue,
                cbsx::WeekDay::kWed,
                cbsx::WeekDay::kThu,
                cbsx::WeekDay::kFri,
            }),
        },
        // Days range enabled, but end in midnight
        // => that range is in step bars without end day
        TestGetStepBarsParams{
            CreateRule({
                cbsx::GoalScheduleItem{
                    cbsx::WeekDay::kTue,
                    "00:00",
                    kCounter,
                },
                cbsx::GoalScheduleItem{
                    cbsx::WeekDay::kFri,
                    "00:00",
                    "0",
                },
            }),
            CreateStepBars({
                cbsx::WeekDay::kTue,
                cbsx::WeekDay::kWed,
                cbsx::WeekDay::kThu,
            }),
        },
        // Multiple ranges enabled,wed is between two
        // enabled ranges, and fri with midnight end
        // => wed and fri are not in step bars
        TestGetStepBarsParams{
            CreateRule({
                cbsx::GoalScheduleItem{
                    cbsx::WeekDay::kMon,
                    "12:00",
                    kCounter,
                },
                cbsx::GoalScheduleItem{
                    cbsx::WeekDay::kTue,
                    "12:00",
                    "0",
                },
                cbsx::GoalScheduleItem{
                    cbsx::WeekDay::kThu,
                    "12:00",
                    kCounter,
                },
                cbsx::GoalScheduleItem{
                    cbsx::WeekDay::kFri,
                    "00:00",
                    "0",
                },
                cbsx::GoalScheduleItem{
                    cbsx::WeekDay::kSat,
                    "00:00",
                    kCounter,
                },
                cbsx::GoalScheduleItem{
                    cbsx::WeekDay::kSun,
                    "23:59",
                    "0",
                },
            }),
            CreateStepBars({
                cbsx::WeekDay::kMon,
                cbsx::WeekDay::kTue,
                cbsx::WeekDay::kThu,
                cbsx::WeekDay::kSat,
                cbsx::WeekDay::kSun,
            }),
        },
        // No null schedules
        // => all week is in step bars because looping
        TestGetStepBarsParams{
            CreateRule({
                cbsx::GoalScheduleItem{
                    cbsx::WeekDay::kWed,
                    "00:00",
                    kCounter,
                },
            }),
            CreateStepBars({
                cbsx::WeekDay::kMon,
                cbsx::WeekDay::kTue,
                cbsx::WeekDay::kWed,
                cbsx::WeekDay::kThu,
                cbsx::WeekDay::kFri,
                cbsx::WeekDay::kSat,
                cbsx::WeekDay::kSun,
            }),
        },
        // Sun has last not null schedule,
        // mon and tue not enabled explicitly
        // => mon and tue are in step bars because looping
        TestGetStepBarsParams{
            CreateRule({
                cbsx::GoalScheduleItem{
                    cbsx::WeekDay::kWed,
                    "12:00",
                    kCounter,
                },
                cbsx::GoalScheduleItem{
                    cbsx::WeekDay::kThu,
                    "12:00",
                    "0",
                },
                cbsx::GoalScheduleItem{
                    cbsx::WeekDay::kSun,
                    "12:00",
                    kCounter,
                },
            }),
            CreateStepBars({
                cbsx::WeekDay::kMon,
                cbsx::WeekDay::kTue,
                cbsx::WeekDay::kWed,
                cbsx::WeekDay::kThu,
                cbsx::WeekDay::kSun,
            }),
        },
        // Sat has last not null schedule,
        // mon and tue not enabled explicitly
        // => mon and tue are in step bars because looping
        TestGetStepBarsParams{
            CreateRule({
                cbsx::GoalScheduleItem{
                    cbsx::WeekDay::kWed,
                    "12:00",
                    kCounter,
                },
                cbsx::GoalScheduleItem{
                    cbsx::WeekDay::kThu,
                    "12:00",
                    "0",
                },
                cbsx::GoalScheduleItem{
                    cbsx::WeekDay::kSat,
                    "12:00",
                    kCounter,
                },
            }),
            CreateStepBars({
                cbsx::WeekDay::kMon,
                cbsx::WeekDay::kTue,
                cbsx::WeekDay::kWed,
                cbsx::WeekDay::kThu,
                cbsx::WeekDay::kSat,
                cbsx::WeekDay::kSun,
            }),
        },
        // Sun has last null schedule,
        // mon and tue not enabled explicitly
        // => mon and tue are not in step bars
        TestGetStepBarsParams{
            CreateRule({
                cbsx::GoalScheduleItem{
                    cbsx::WeekDay::kWed,
                    "12:00",
                    kCounter,
                },
                cbsx::GoalScheduleItem{
                    cbsx::WeekDay::kThu,
                    "12:00",
                    "0",
                },
                cbsx::GoalScheduleItem{
                    cbsx::WeekDay::kSun,
                    "12:00",
                    kCounter,
                },
                cbsx::GoalScheduleItem{
                    cbsx::WeekDay::kSun,
                    "21:00",
                    "0",
                },
            }),
            CreateStepBars({
                cbsx::WeekDay::kWed,
                cbsx::WeekDay::kThu,
                cbsx::WeekDay::kSun,
            }),
        },
        // Mon has only one null schedule, but not midnight,
        // sun has enabled last schedule, so looping
        // => mon is in range, tue is not in range
        TestGetStepBarsParams{
            CreateRule({
                cbsx::GoalScheduleItem{
                    cbsx::WeekDay::kMon,
                    "12:00",
                    "0",
                },
                cbsx::GoalScheduleItem{
                    cbsx::WeekDay::kWed,
                    "12:00",
                    kCounter,
                },
                cbsx::GoalScheduleItem{
                    cbsx::WeekDay::kThu,
                    "12:00",
                    "0",
                },
                cbsx::GoalScheduleItem{
                    cbsx::WeekDay::kSun,
                    "12:00",
                    kCounter,
                },
            }),
            CreateStepBars({
                cbsx::WeekDay::kMon,
                cbsx::WeekDay::kWed,
                cbsx::WeekDay::kThu,
                cbsx::WeekDay::kSun,
            }),
        },
        // Mon has only one null schedule, but midnight,
        // sun has enabled last schedule, so looping
        // => mon and tue are not in range
        TestGetStepBarsParams{
            CreateRule({
                cbsx::GoalScheduleItem{
                    cbsx::WeekDay::kMon,
                    "00:00",
                    "0",
                },
                cbsx::GoalScheduleItem{
                    cbsx::WeekDay::kWed,
                    "12:00",
                    kCounter,
                },
                cbsx::GoalScheduleItem{
                    cbsx::WeekDay::kThu,
                    "12:00",
                    "0",
                },
                cbsx::GoalScheduleItem{
                    cbsx::WeekDay::kSun,
                    "12:00",
                    kCounter,
                },
            }),
            CreateStepBars({
                cbsx::WeekDay::kWed,
                cbsx::WeekDay::kThu,
                cbsx::WeekDay::kSun,
            }),
        }));

}  // namespace tests
