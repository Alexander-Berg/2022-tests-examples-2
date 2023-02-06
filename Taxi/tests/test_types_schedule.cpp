#include <gmock/gmock.h>

#include "smart_rules/types/base_types.hpp"
#include "smart_rules/types/schedule.hpp"
#include "smart_rules/validators/schedule.hpp"

namespace vs = billing_subventions_x::smart_rules::validators;
namespace types = billing_subventions_x::types;

using Schedule = billing_subventions_x::types::Schedule;
using Weekday = billing_subventions_x::types::WeekDay;

TEST(ASchedule, StillValidAfterLoopingWhenStartsFromTheBeginingOfTheWeek) {
  auto schedule =
      Schedule{{Weekday::kMon, "00:00", "1"}, {Weekday::kMon, "18:00", "0"}};
  types::LoopSchedule(schedule);
  ASSERT_NO_THROW(vs::ValidateSchedule(schedule));
}

TEST(ASchedule, StillValidAfterLoopingWhenEndsAtTheEndingOfTheWeek) {
  auto schedule =
      Schedule{{Weekday::kSun, "18:00", "1"}, {Weekday::kSun, "24:00", "0"}};
  types::LoopSchedule(schedule);
  ASSERT_NO_THROW(vs::ValidateSchedule(schedule));
}
