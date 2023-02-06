#include <gmock/gmock.h>

#include "smart_rules/types/base_types.hpp"
#include "smart_rules/types/schedule.hpp"
#include "smart_rules/validators/exceptions.hpp"
#include "smart_rules/validators/schedule.hpp"

namespace vs = billing_subventions_x::smart_rules::validators;

using Schedule = billing_subventions_x::types::Schedule;
using Weekday = billing_subventions_x::types::WeekDay;

TEST(ScheduleValidator, SilentlyPassesWhenOk) {
  auto schedule =
      Schedule{{Weekday::kMon, "12:00", "1"}, {Weekday::kMon, "13:00", "0"}};
  ASSERT_NO_THROW(vs::ValidateSchedule(schedule));
}

TEST(ScheduleValidator, ThrowsExceptionWhenTimeIsInvalid) {
  auto schedule = Schedule{{Weekday::kMon, "25:00", "1"}};
  try {
    vs::ValidateSchedule(schedule);
    FAIL();
  } catch (const vs::ValidationError& exc) {
    const std::string expected =
        "Cutoff with wrong start time: week_day = mon, time = 25:00";
    ASSERT_THAT(std::string(exc.what()), ::testing::Eq(expected));
  }
}

TEST(ScheduleValidator, ThrowsExceptionWhenThereIsDuplicatedCutoff) {
  auto schedule = Schedule{{Weekday::kMon, "00:00", "1"},
                           {Weekday::kMon, "18:00", "0"},
                           {Weekday::kSun, "18:00", "2"},
                           {Weekday::kMon, "00:00", "0"}};
  try {
    vs::ValidateSchedule(schedule);
    FAIL();
  } catch (const vs::ValidationError& exc) {
    const std::string expected =
        "Duplicated cutoff: week_day = mon, time = 00:00";
    ASSERT_THAT(std::string(exc.what()), ::testing::Eq(expected));
  }
}
