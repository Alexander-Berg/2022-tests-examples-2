#include <gtest/gtest.h>

#include <userver/utils/datetime.hpp>

#include <pricing-components/utils/schedule.hpp>

namespace {

using Dates = decltype(std::declval<models::Country>().holidays);
using Weekends = decltype(std::declval<models::Country>().weekends);
using Weekday = clients::territories::CountryWeekendsA;

const Weekends kSatSun{{Weekday::kSaturday, Weekday::kSunday}};
const Dates kWorkdays2018{{"2018-04-28", "2018-06-09", "2018-12-29"}};
const Dates kHolidays2018{
    {"2018-01-01", "2018-01-02", "2018-01-03", "2018-01-04", "2018-01-05",
     "2018-01-06", "2018-01-07", "2018-01-08", "2018-02-23", "2018-03-08",
     "2018-03-09", "2018-04-30", "2018-05-01", "2018-05-02", "2018-05-09",
     "2018-06-11", "2018-06-12", "2018-11-05", "2018-12-31"}};

struct ScheduleParams {
  Weekends weekends;
  Dates holidays;
  Dates workdays;
};

const ScheduleParams kEmpty{std::nullopt, std::nullopt, std::nullopt};
const ScheduleParams kWeekends{kSatSun, std::nullopt, std::nullopt};
const ScheduleParams kSchedule2018{kSatSun, kHolidays2018, kWorkdays2018};

using ScheduleChecks = std::tuple<ScheduleParams, std::string, bool>;

const bool kIsDayoff = true;

}  // namespace

class DaysOffChecker : public ::testing::TestWithParam<ScheduleChecks> {};

TEST_P(DaysOffChecker, DaysOffChecker) {
  namespace dt = utils::datetime;

  const auto& [schedule_params, datestring, is_dayoff] = GetParam();
  const models::Country country{{},
                                {},
                                {},
                                {},
                                schedule_params.weekends,
                                schedule_params.holidays,
                                schedule_params.workdays};
  const utils::Schedule schedule(country);
  const auto& timestamp =
      dt::Stringtime(datestring, dt::kDefaultDriverTimezone, "%Y-%m-%d");
  EXPECT_EQ(schedule.IsDayoff(timestamp, dt::kDefaultDriverTimezone),
            is_dayoff);
}

INSTANTIATE_TEST_SUITE_P(
    DaysOffChecker, DaysOffChecker,
    ::testing::Values(  //
        std::make_tuple(kEmpty, "2019-08-03", !kIsDayoff),
        std::make_tuple(kWeekends, "2019-08-01", !kIsDayoff),
        std::make_tuple(kWeekends, "2019-08-03", kIsDayoff),
        std::make_tuple(kSchedule2018, "2018-01-02", kIsDayoff),
        std::make_tuple(kSchedule2018, "2018-02-02", !kIsDayoff),
        std::make_tuple(kSchedule2018, "2018-04-02", !kIsDayoff),
        std::make_tuple(kSchedule2018, "2018-05-02", kIsDayoff),
        std::make_tuple(kSchedule2018, "2018-06-02", kIsDayoff),
        std::make_tuple(kSchedule2018, "2018-06-09", !kIsDayoff)));
