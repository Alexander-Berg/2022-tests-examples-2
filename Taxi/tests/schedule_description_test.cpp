#include <gtest/gtest.h>

// https://bb.yandex-team.ru/projects/EDA/repos/backend_service_core/browse/src/AppBundle/Tests/Service/Scheduler/DescriptionGeneratorTest.php#11

#include <utils/schedule/schedule_description.hpp>

#include <utils/schedule/tests/utils.hpp>

namespace eats_restaurant_menu::utils::schedule::tests {

namespace {

using namespace std::chrono_literals;
namespace tanker_keys = localization::keys::category_schedule;

const std::unordered_map<localization::TankerKey, std::string>
    kMockLocalization{
        {tanker_keys::kMonday, "Пн"},
        {tanker_keys::kTuesday, "Вт"},
        {tanker_keys::kWednesday, "Ср"},
        {tanker_keys::kThursday, "Чт"},
        {tanker_keys::kFriday, "Пт"},
        {tanker_keys::kSaturday, "Сб"},
        {tanker_keys::kSunday, "Вс"},
        {tanker_keys::kWeekdays, "По будням"},
        {tanker_keys::kHolidays, "По выходным"},
        {tanker_keys::kDayRange, "{start} - {end}"},
        {tanker_keys::kFrom, "с {time}"},
        {tanker_keys::kUntil, "до {time}"},
        {tanker_keys::kFromUntil, "с {from} до {to}"},
        {tanker_keys::kDaysIntervals, "{days} {intervals}"},
    };

DescriptionGenerator MakeDescriptionGenerator() {
  static const ScheduleLocalizer localizer{
      localization::MakeTestLocalizer(kMockLocalization)};
  constexpr static const size_t kMaxLength = 100;
  return DescriptionGenerator{localizer, kMaxLength};
}

struct TestCase {
  std::string name;
  DaySchedules schedules;
  DaySchedules borders;
  std::optional<std::string> expected;
};

DaySchedules MakeBorders() {
  Schedules schedules;
  for (const auto week_day : kWeekDays) {
    // 08:00 - 20:00
    schedules.push_back(Schedule{week_day, 8h, 20h});
  }
  return ToDaySchedule(schedules);
}

class DescriptionGeneratorTest : public ::testing::TestWithParam<TestCase> {};

}  // namespace

TEST_P(DescriptionGeneratorTest, DescriptionGenerator) {
  const auto generator = MakeDescriptionGenerator();
  const auto params = GetParam();
  const auto result =
      generator.MakeDescription(params.schedules, params.borders);
  ASSERT_EQ(result, params.expected) << result.value_or("null");
}

INSTANTIATE_TEST_SUITE_P(
    /**/, DescriptionGeneratorTest,
    ::testing::Values(
        TestCase{
            "empty",       // name
            {},            // schedules
            {},            // borders
            std::nullopt,  // expected
        },
        TestCase{
            "two_borders_same_day_schedule",  // name
            ToDaySchedule({
                Schedule{cctz::weekday::monday, 11h, 16h},
            }),  // schedules
            ToDaySchedule({
                Schedule{cctz::weekday::monday, 0h, 3h},
                Schedule{cctz::weekday::monday, 11h, 24h},
            }),             // borders
            "Пн до 16:00",  // expected
        },
        TestCase{
            "two_borders_two_same_day_schedule_different_time",  // name
            ToDaySchedule({
                Schedule{cctz::weekday::monday, 0h, 2h + 30min},
                Schedule{cctz::weekday::monday, 14h, 16h},
            }),  // schedules
            ToDaySchedule({
                Schedule{cctz::weekday::monday, 0h, 3h},
                Schedule{cctz::weekday::monday, 11h, 24h},
            }),                               // borders
            "Пн до 02:30, с 14:00 до 16:00",  // expected
        },
        TestCase{
            "two_borders_two_days_same_time",  // name
            ToDaySchedule({
                Schedule{cctz::weekday::monday, 0h, 3h},
                Schedule{cctz::weekday::tuesday, 0h, 3h},
            }),  // schedules
            ToDaySchedule({
                Schedule{cctz::weekday::monday, 11h, 24h},
                Schedule{cctz::weekday::monday, 0h, 3h},
                Schedule{cctz::weekday::tuesday, 11h, 24h},
                Schedule{cctz::weekday::tuesday, 0h, 3h},
            }),         // borders
            "Пн - Вт",  // expected
        },
        TestCase{
            "monday",  // name
            ToDaySchedule({
                Schedule{cctz::weekday::monday, 12h, 20h + 20min},
            }),                     // schedules
            {},                     // borders
            "Пн с 12:00 до 20:20",  // expected
        },
        TestCase{
            "monday_diff_interval",  // name
            ToDaySchedule({
                Schedule{cctz::weekday::monday, 9h, 9h + 30min},
                Schedule{cctz::weekday::monday, 10h, 10h + 30min},
                Schedule{cctz::weekday::monday, 11h, 11h + 30min},
            }),  // schedules
            {},  // borders
            "Пн с 09:00 до 09:30, с 10:00 до 10:30, с 11:00 до 11:30",  // expected
        },
        TestCase{
            "same_day_same_hour",  // name
            ToDaySchedule({
                Schedule{cctz::weekday::monday, 12h, 20h + 20min},
                Schedule{cctz::weekday::wednesday, 11h, 19h + 20min},
                Schedule{cctz::weekday::friday, 12h, 17h},
            }),  // schedules
            {},  // borders
            "Пн с 12:00 до 20:20, Ср с 11:00 до 19:20, Пт с 12:00 до 17:00",  // expected
        },
        TestCase{
            "same_day_diff_hours",  // name
            ToDaySchedule({
                Schedule{cctz::weekday::monday, 12h, 13h + 30min},
                Schedule{cctz::weekday::monday, 14h, 15h + 30min},
                Schedule{cctz::weekday::wednesday, 13h, 14h + 30min},
                Schedule{cctz::weekday::wednesday, 15h, 16h + 30min},
            }),  // schedules
            {},  // borders
            "Пн с 12:00 до 13:30, с 14:00 до 15:30, Ср с 13:00 до 14:30, с "
            "15:00 до 16:30",  // expected
        },
        TestCase{
            "same_day_equal_hour",  // name
            ToDaySchedule({
                Schedule{cctz::weekday::monday, 12h, 17h},
                Schedule{cctz::weekday::wednesday, 12h, 17h},
                Schedule{cctz::weekday::friday, 12h, 17h},
            }),                             // schedules
            {},                             // borders
            "Пн, Ср, Пт с 12:00 до 17:00",  // expected
        },
        TestCase{
            "weekdays_and_holidays_separately",  // name
            ToDaySchedule({
                Schedule{cctz::weekday::monday, 12h, 20h + 20min},
                Schedule{cctz::weekday::tuesday, 12h, 20h + 20min},
                Schedule{cctz::weekday::wednesday, 12h, 20h + 20min},
                Schedule{cctz::weekday::thursday, 12h, 20h + 20min},
                Schedule{cctz::weekday::friday, 12h, 20h + 20min},
                Schedule{cctz::weekday::saturday, 13h, 21h + 20min},
                Schedule{cctz::weekday::sunday, 13h, 21h + 20min},
            }),  // schedules
            {},  // borders
            "По будням с 12:00 до 20:20, По выходным с 13:00 до 21:20",  // expected
        },
        TestCase{
            "weekday_only",  // name
            ToDaySchedule({
                Schedule{cctz::weekday::monday, 12h, 20h + 20min},
                Schedule{cctz::weekday::tuesday, 12h, 20h + 20min},
                Schedule{cctz::weekday::wednesday, 12h, 20h + 20min},
                Schedule{cctz::weekday::thursday, 12h, 20h + 20min},
                Schedule{cctz::weekday::friday, 12h, 20h + 20min},
            }),                            // schedules
            {},                            // borders
            "По будням с 12:00 до 20:20",  // expected
        },
        TestCase{
            "holiday_only",  // name
            ToDaySchedule({
                Schedule{cctz::weekday::saturday, 13h, 21h + 20min},
                Schedule{cctz::weekday::sunday, 13h, 21h + 20min},
            }),                              // schedules
            {},                              // borders
            "По выходным с 13:00 до 21:20",  // expected
        },
        TestCase{
            "everyday_single_interval",  // name
            ToDaySchedule({
                Schedule{cctz::weekday::monday, 12h, 14h},
                Schedule{cctz::weekday::tuesday, 12h, 14h},
                Schedule{cctz::weekday::wednesday, 12h, 14h},
                Schedule{cctz::weekday::thursday, 12h, 14h},
                Schedule{cctz::weekday::friday, 12h, 14h},
                Schedule{cctz::weekday::saturday, 12h, 14h},
                Schedule{cctz::weekday::sunday, 12h, 14h},
            }),                  // schedules
            {},                  // borders
            "с 12:00 до 14:00",  // expected
        },
        TestCase{
            "everyday_double_interval",  // name
            ToDaySchedule({
                Schedule{cctz::weekday::monday, 12h, 14h},
                Schedule{cctz::weekday::monday, 16h, 18h},
                Schedule{cctz::weekday::tuesday, 12h, 14h},
                Schedule{cctz::weekday::tuesday, 16h, 18h},
                Schedule{cctz::weekday::wednesday, 12h, 14h},
                Schedule{cctz::weekday::wednesday, 16h, 18h},
                Schedule{cctz::weekday::thursday, 12h, 14h},
                Schedule{cctz::weekday::thursday, 16h, 18h},
                Schedule{cctz::weekday::friday, 12h, 14h},
                Schedule{cctz::weekday::friday, 16h, 18h},
                Schedule{cctz::weekday::saturday, 12h, 14h},
                Schedule{cctz::weekday::saturday, 16h, 18h},
                Schedule{cctz::weekday::sunday, 12h, 14h},
                Schedule{cctz::weekday::sunday, 16h, 18h},
            }),                                    // schedules
            {},                                    // borders
            "с 12:00 до 14:00, с 16:00 до 18:00",  // expected
        },
        TestCase{
            "merge_and_range",  // name
            ToDaySchedule({
                Schedule{cctz::weekday::monday, 0h, 24h},
                Schedule{cctz::weekday::tuesday, 12h, 20h + 20min},
                Schedule{cctz::weekday::wednesday, 12h, 20h + 20min},
                Schedule{cctz::weekday::thursday, 12h, 20h + 20min},
                Schedule{cctz::weekday::friday, 0h, 24h},
            }),                                                   // schedules
            {},                                                   // borders
            "Пн, Пт с 00:00 до 24:00, Вт - Чт с 12:00 до 20:20",  // expected
        },
        TestCase{
            "merge_and_holyday_group",  // name
            ToDaySchedule({
                Schedule{cctz::weekday::monday, 12h, 20h + 20min},
                Schedule{cctz::weekday::tuesday, 12h, 20h + 20min},
                Schedule{cctz::weekday::wednesday, 12h, 20h + 20min},
                Schedule{cctz::weekday::saturday, 12h, 20h + 20min},
                Schedule{cctz::weekday::sunday, 12h, 20h + 20min},
            }),                                       // schedules
            {},                                       // borders
            "Пн - Ср, По выходным с 12:00 до 20:20",  // expected
        },
        TestCase{
            "merge_and_stabdalone_sunday",  // name
            ToDaySchedule({
                Schedule{cctz::weekday::monday, 12h, 20h + 20min},
                Schedule{cctz::weekday::tuesday, 12h, 20h + 20min},
                Schedule{cctz::weekday::wednesday, 12h, 20h + 20min},
                Schedule{cctz::weekday::saturday, 12h, 20h + 20min},
                Schedule{cctz::weekday::sunday, 0h, 24h},
            }),                                                   // schedules
            {},                                                   // borders
            "Пн - Ср, Сб с 12:00 до 20:20, Вс с 00:00 до 24:00",  // expected
        },
        TestCase{
            "monday_and_holidays",  // name
            ToDaySchedule({
                Schedule{cctz::weekday::monday, 12h, 20h + 20min},
                Schedule{cctz::weekday::saturday, 12h, 20h + 20min},
                Schedule{cctz::weekday::sunday, 12h, 20h + 20min},
            }),                                  // schedules
            {},                                  // borders
            "Пн, По выходным с 12:00 до 20:20",  // expected
        },
        TestCase{
            "weekdays_and_sunday",  // name
            ToDaySchedule({
                Schedule{cctz::weekday::monday, 12h, 20h + 20min},
                Schedule{cctz::weekday::tuesday, 12h, 20h + 20min},
                Schedule{cctz::weekday::wednesday, 12h, 20h + 20min},
                Schedule{cctz::weekday::thursday, 12h, 20h + 20min},
                Schedule{cctz::weekday::friday, 12h, 20h + 20min},
                Schedule{cctz::weekday::sunday, 12h, 20h + 20min},
            }),                                // schedules
            {},                                // borders
            "По будням, Вс с 12:00 до 20:20",  // expected
        },
        TestCase{
            "whole_week_two_weekday_and_holiday",  // name
            ToDaySchedule({
                Schedule{cctz::weekday::monday, 12h, 20h},
                Schedule{cctz::weekday::tuesday, 12h, 20h},
                Schedule{cctz::weekday::wednesday, 12h, 14h},
                Schedule{cctz::weekday::thursday, 12h, 14h},
                Schedule{cctz::weekday::friday, 12h, 14h},
                Schedule{cctz::weekday::saturday, 12h, 14h},
                Schedule{cctz::weekday::sunday, 12h, 14h},
            }),                                                    // schedules
            {},                                                    // borders
            "Пн - Вт с 12:00 до 20:00, Ср - Вс с 12:00 до 14:00",  // expected
        },
        TestCase{
            "whole_week_two_weekday_and_weekday_holiday",  // name
            ToDaySchedule({
                Schedule{cctz::weekday::monday, 12h, 20h},
                Schedule{cctz::weekday::tuesday, 12h, 20h},
                Schedule{cctz::weekday::wednesday, 12h, 20h},
                Schedule{cctz::weekday::thursday, 12h, 20h},
                Schedule{cctz::weekday::friday, 12h, 14h},
                Schedule{cctz::weekday::saturday, 12h, 20h},
                Schedule{cctz::weekday::sunday, 12h, 14h},
            }),  // schedules
            {},  // borders
            "Пн - Чт, Сб с 12:00 до 20:00, Пт, Вс с 12:00 до 14:00",  // expected
        },
        TestCase{
            "weekdays_will_not_merge",  // name
            ToDaySchedule({
                Schedule{cctz::weekday::monday, 12h, 13h},
                Schedule{cctz::weekday::monday, 14h, 16h},
                Schedule{cctz::weekday::friday, 14h, 16h},
            }),  // schedules
            {},  // borders
            "Пн с 12:00 до 13:00, с 14:00 до 16:00, Пт с 14:00 до 16:00",  // expected
        },
        TestCase{
            "days_will_merge",  // name
            ToDaySchedule({
                Schedule{cctz::weekday::monday, 12h, 13h},
                Schedule{cctz::weekday::monday, 14h, 16h},
                Schedule{cctz::weekday::tuesday, 12h, 13h},
                Schedule{cctz::weekday::tuesday, 14h, 16h},
                Schedule{cctz::weekday::wednesday, 12h, 13h},
                Schedule{cctz::weekday::wednesday, 14h, 16h},
            }),                                            // schedules
            {},                                            // borders
            "Пн - Ср с 12:00 до 13:00, с 14:00 до 16:00",  // expected
        },
        TestCase{
            "weekdays_starts_with_place",  // name
            ToDaySchedule({
                Schedule{cctz::weekday::monday, 12h, 22h},
                Schedule{cctz::weekday::tuesday, 12h, 22h},
                Schedule{cctz::weekday::wednesday, 12h, 22h},
                Schedule{cctz::weekday::thursday, 12h, 22h},
                Schedule{cctz::weekday::friday, 12h, 22h},
                Schedule{cctz::weekday::saturday, 13h, 23h},
                Schedule{cctz::weekday::sunday, 13h, 23h},
            }),  // schedules
            ToDaySchedule({
                Schedule{cctz::weekday::monday, 12h, 24h},
                Schedule{cctz::weekday::tuesday, 12h, 24h},
                Schedule{cctz::weekday::wednesday, 12h, 24h},
                Schedule{cctz::weekday::thursday, 12h, 24h},
                Schedule{cctz::weekday::friday, 12h, 24h},
                Schedule{cctz::weekday::saturday, 12h, 24h},
                Schedule{cctz::weekday::sunday, 12h, 24h},
            }),                                                  // borders
            "По будням до 22:00, По выходным с 13:00 до 23:00",  // expected
        },
        TestCase{
            "tuesday_is_diffrent_from_single_place_interval",  // name
            ToDaySchedule({
                Schedule{cctz::weekday::monday, 12h, 20h},
                Schedule{cctz::weekday::tuesday, 12h, 22h},
                Schedule{cctz::weekday::wednesday, 12h, 20h},
                Schedule{cctz::weekday::thursday, 12h, 20h},
                Schedule{cctz::weekday::friday, 12h, 20h},
            }),  // schedules
            ToDaySchedule({
                Schedule{cctz::weekday::monday, 10h, 22h},
                Schedule{cctz::weekday::tuesday, 10h, 20h},
                Schedule{cctz::weekday::wednesday, 10h, 22h},
                Schedule{cctz::weekday::thursday, 10h, 22h},
                Schedule{cctz::weekday::friday, 10h, 22h},
                Schedule{cctz::weekday::saturday, 10h, 22h},
                Schedule{cctz::weekday::sunday, 10h, 22h},
            }),                                          // borders
            "Пн, Ср - Пт с 12:00 до 20:00, Вт с 12:00",  // expected
        },
        TestCase{
            "both_sides_different",  // name
            ToDaySchedule({
                Schedule{cctz::weekday::monday, 12h, 13h + 40min},
                Schedule{cctz::weekday::sunday, 12h, 13h + 40min},
            }),                         // schedules
            {},                         // borders
            "Пн, Вс с 12:00 до 13:40",  // expected
        },
        TestCase{
            "weekdays",  // name
            ToDaySchedule({
                Schedule{cctz::weekday::monday, 8h, 20h},
                Schedule{cctz::weekday::tuesday, 8h, 20h},
                Schedule{cctz::weekday::wednesday, 8h, 20h},
                Schedule{cctz::weekday::thursday, 8h, 20h},
                Schedule{cctz::weekday::friday, 8h, 20h},
            }),             // schedules
            MakeBorders(),  // borders
            "По будням",    // expected
        },
        TestCase{
            "holidays",  // name
            ToDaySchedule({
                Schedule{cctz::weekday::saturday, 8h, 20h},
                Schedule{cctz::weekday::sunday, 8h, 20h},
            }),             // schedules
            MakeBorders(),  // borders
            "По выходным",  // expected
        },
        TestCase{
            "monday_holidays",  // name
            ToDaySchedule({
                Schedule{cctz::weekday::monday, 8h, 20h},
                Schedule{cctz::weekday::saturday, 8h, 20h},
                Schedule{cctz::weekday::sunday, 8h, 20h},
            }),                 // schedules
            MakeBorders(),      // borders
            "Пн, По выходным",  // expected
        },
        TestCase{
            "start_and_end_same",  // name
            ToDaySchedule({
                Schedule{cctz::weekday::monday, 10h, 12h},
                Schedule{cctz::weekday::tuesday, 10h, 12h},
                Schedule{cctz::weekday::wednesday, 10h, 12h},
                Schedule{cctz::weekday::thursday, 10h, 12h},
                Schedule{cctz::weekday::friday, 10h, 12h},
            }),                            // schedules
            MakeBorders(),                 // borders
            "По будням с 10:00 до 12:00",  // expected
        },
        TestCase{
            "only_end_different",  // name
            ToDaySchedule({
                Schedule{cctz::weekday::monday, 8h, 12h},
                Schedule{cctz::weekday::tuesday, 8h, 12h},
                Schedule{cctz::weekday::wednesday, 8h, 12h},
                Schedule{cctz::weekday::thursday, 8h, 12h},
                Schedule{cctz::weekday::friday, 8h, 12h},
            }),                    // schedules
            MakeBorders(),         // borders
            "По будням до 12:00",  // expected
        },
        TestCase{
            "only_begin_different",  // name
            ToDaySchedule({
                Schedule{cctz::weekday::monday, 16h, 20h},
                Schedule{cctz::weekday::tuesday, 16h, 20h},
                Schedule{cctz::weekday::wednesday, 16h, 20h},
                Schedule{cctz::weekday::thursday, 16h, 20h},
                Schedule{cctz::weekday::friday, 16h, 20h},
            }),                   // schedules
            MakeBorders(),        // borders
            "По будням с 16:00",  // expected
        }),
    [](const auto& v) { return v.param.name; });

}  // namespace eats_restaurant_menu::utils::schedule::tests
