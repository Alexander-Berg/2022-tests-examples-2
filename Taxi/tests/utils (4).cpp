#include "utils.hpp"

namespace eats_restaurant_menu::utils::schedule::tests {

DaySchedules ToDaySchedule(Schedules schedules) {
  DaySchedules result;
  for (const auto& schedule : schedules) {
    result[schedule.week_day].push_back(schedule);
  }
  return result;
}

}  // namespace eats_restaurant_menu::utils::schedule::tests
