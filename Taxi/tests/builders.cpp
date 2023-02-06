#include "builders.hpp"

#include <string>

#include <fmt/format.h>

#include <userver/utils/datetime.hpp>

#include "smart_rules/types/base_types.hpp"

using TimePoint = billing_subventions_x::types::TimePoint;

TimePoint ATimePoint(const std::string& value) {
  return utils::datetime::GuessStringtime(value, "UTC");
}

std::string TimePointsNotEqual(TimePoint actual, TimePoint expected) {
  return fmt::format("Timepoints not equal. Actual: {}. Expected: {}",
                     utils::datetime::Timestring(actual),
                     utils::datetime::Timestring(expected));
}
