#include <gtest/gtest.h>

#include <utils/schedule/schedule_localizer.hpp>

namespace eats_restaurant_menu::utils::schedule::tests {

using namespace std::chrono_literals;
namespace tanker_keys = localization::keys::category_schedule;

const std::unordered_map<localization::TankerKey, std::string>
    kMockLocalization{
        {tanker_keys::kMonday, "Пн"},
        {tanker_keys::kTuesday, "Вт"},
        {tanker_keys::kFriday, "Пт"},
        {tanker_keys::kSaturday, "Вт"},
        {tanker_keys::kSunday, "Вс"},
        {tanker_keys::kWeekdays, "По будням"},
        {tanker_keys::kHolidays, "По выходным"},
        {tanker_keys::kDayRange, "{start} - {end}"},
        {tanker_keys::kFrom, "с {time}"},
        {tanker_keys::kUntil, "до {time}"},
    };

struct IntervalTestCase {
  std::string name;
  cctz::weekday start;
  cctz::weekday end;
  std::string expected;
};

class ScheduleLocalizerIntervalTest
    : public ::testing::TestWithParam<IntervalTestCase> {};

TEST_P(ScheduleLocalizerIntervalTest, TranslateInterval) {
  auto params = GetParam();
  const ScheduleLocalizer localizer{
      localization::MakeTestLocalizer(kMockLocalization)};

  const auto result = localizer.TranslateInterval(params.start, params.end);
  ASSERT_EQ(result, params.expected);
}

INSTANTIATE_TEST_SUITE_P(
    /**/, ScheduleLocalizerIntervalTest,
    ::testing::Values(
        IntervalTestCase{
            "whole_week",           // name
            cctz::weekday::monday,  // start
            cctz::weekday::sunday,  // end
            "",                     // expected
        },
        IntervalTestCase{
            "range",                 // name
            cctz::weekday::monday,   // start
            cctz::weekday::tuesday,  // end
            "Пн - Вт",               // expected
        },
        IntervalTestCase{
            "weekdays",             // name
            cctz::weekday::monday,  // start
            cctz::weekday::friday,  // end
            "По будням",            // expected
        },
        IntervalTestCase{
            "holidays",               // name
            cctz::weekday::saturday,  // start
            cctz::weekday::sunday,    // end
            "По выходным",            // expected
        }),
    [](const auto& v) { return v.param.name; });

struct TimeTestCase {
  std::string name;
  std::chrono::minutes time;
  std::string expected;
};

class ScheduleLocalizerTimeTest
    : public ::testing::TestWithParam<TimeTestCase> {};

TEST_P(ScheduleLocalizerTimeTest, TranslateTo) {
  auto params = GetParam();

  const ScheduleLocalizer localizer{
      localization::MakeTestLocalizer(kMockLocalization)};

  const auto result = localizer.TranslateTo(params.time);
  ASSERT_EQ(result, params.expected);
}

INSTANTIATE_TEST_SUITE_P(
    /**/, ScheduleLocalizerTimeTest,
    ::testing::Values(
        TimeTestCase{
            "generic",   // name
            5h,          // time
            "до 05:00",  // expected
        },
        TimeTestCase{
            "24",  // name
            24h,
            "до 24:00",  // expected
        }),
    [](const auto& v) { return v.param.name; });

}  // namespace eats_restaurant_menu::utils::schedule::tests
