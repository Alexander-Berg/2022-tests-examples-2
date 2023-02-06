#include <gmock/gmock.h>

#include "smart_rules/types/goal/counter.hpp"
#include "smart_rules/validators/counters.hpp"
#include "smart_rules/validators/exceptions.hpp"

namespace vs = billing_subventions_x::smart_rules::validators;

using CounterSteps = billing_subventions_x::types::GoalCounterSteps;
using Counters = billing_subventions_x::types::GoalCounters;
using CutOff = billing_subventions_x::types::GoalScheduleItem;
using Step = billing_subventions_x::types::GoalStep;
using Weekday = billing_subventions_x::types::WeekDay;

TEST(CountersValidator, SilentlyPassesWhenOk) {
  auto schedule = std::vector<CutOff>{{Weekday::kMon, "12:00", "A"},
                                      {Weekday::kMon, "13:00", "0"},
                                      {Weekday::kMon, "18:00", "B"},
                                      {Weekday::kMon, "19:00", "0"}};
  auto steps = std::vector<CounterSteps>{{"A", {{10, "100"}, {20, "200"}}},
                                         {"B", {{15, "150"}, {20, "300"}}}};
  ASSERT_NO_THROW(vs::ValidateCounters({schedule, steps}));
}

namespace {

void AssertInvalid(const Counters& counters, const std::string& expected) {
  try {
    vs::ValidateCounters(counters);
    FAIL();
  } catch (const vs::ValidationError& exc) {
    ASSERT_THAT(std::string(exc.what()), ::testing::Eq(expected));
  }
}

}  // namespace

TEST(CountersValidator, ThrowsExceptionWhenCounterNotFoundInSchedule) {
  auto schedule = std::vector<CutOff>{{Weekday::kMon, "12:00", "A"},
                                      {Weekday::kMon, "13:00", "0"}};
  auto steps = std::vector<CounterSteps>{{"A", {{10, "100"}, {20, "200"}}},
                                         {"B", {{15, "150"}, {20, "300"}}}};
  AssertInvalid({schedule, steps}, "B: has steps, but no schedule.");
}

TEST(CountersValidator, ThrowsExceptionWhenCounterHasScheduleButNoStepsSet) {
  auto schedule = std::vector<CutOff>{{Weekday::kMon, "12:00", "A"},
                                      {Weekday::kMon, "13:00", "B"},
                                      {Weekday::kMon, "18:00", "C"},
                                      {Weekday::kMon, "19:00", "0"}};
  auto steps = std::vector<CounterSteps>{{"A", {{10, "100"}, {20, "200"}}}};
  AssertInvalid({schedule, steps}, "B, C: has schedule, but no steps.");
}

TEST(CountersValidator, ThrowsExceptionWhenStepsHaveDuplicatedCounters) {
  auto schedule = std::vector<CutOff>{{Weekday::kMon, "12:00", "A"},
                                      {Weekday::kMon, "13:00", "0"}};
  auto steps = std::vector<CounterSteps>{{"A", {{10, "100"}, {20, "200"}}},
                                         {"A", {{10, "100"}, {20, "200"}}}};
  AssertInvalid({schedule, steps}, "A: duplicated steps definition.");
}

TEST(CountersValidator, ThrowsExceptionWhenNridesInStepsDefinitionEqual) {
  auto schedule = std::vector<CutOff>{{Weekday::kMon, "12:00", "A"},
                                      {Weekday::kMon, "13:00", "0"}};
  auto steps = std::vector<CounterSteps>{{"A", {{10, "100"}, {10, "200"}}}};
  AssertInvalid({schedule, steps}, "A: steps must be in ascending order.");
}

TEST(CountersValidator, ThrowsExceptionWhenNridesInStepsDefinitionDecrease) {
  auto schedule = std::vector<CutOff>{{Weekday::kMon, "12:00", "A"},
                                      {Weekday::kMon, "13:00", "0"}};
  auto steps = std::vector<CounterSteps>{{"A", {{10, "100"}, {5, "200"}}}};
  AssertInvalid({schedule, steps}, "A: steps must be in ascending order.");
}

TEST(CountersValidator, ThrowsExceptionWhenAmountsInStepsDefinitionEqual) {
  auto schedule = std::vector<CutOff>{{Weekday::kMon, "12:00", "A"},
                                      {Weekday::kMon, "13:00", "0"}};
  auto steps = std::vector<CounterSteps>{{"A", {{10, "100"}, {15, "100"}}}};
  AssertInvalid({schedule, steps}, "A: amounts must be in ascending order.");
}

TEST(CountersValidator, ThrowsExceptionWhenAmountsInStepsDefinitionDecrease) {
  auto schedule = std::vector<CutOff>{{Weekday::kMon, "12:00", "A"},
                                      {Weekday::kMon, "13:00", "0"}};
  auto steps = std::vector<CounterSteps>{{"A", {{10, "100"}, {15, "50"}}}};
  AssertInvalid({schedule, steps}, "A: amounts must be in ascending order.");
}

TEST(CountersValidator, ThrowsExceptionWhenUseForbiddenValueForCounterID) {
  auto schedule = std::vector<CutOff>{{Weekday::kMon, "12:00", "A"},
                                      {Weekday::kMon, "13:00", "0"}};
  auto steps = std::vector<CounterSteps>{{"A", {{10, "100"}, {15, "150"}}},
                                         {"0", {{10, "100"}}}};
  AssertInvalid({schedule, steps}, "0: forbidden to use as a counter ID.");
}
