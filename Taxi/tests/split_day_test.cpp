#include <gtest/gtest.h>

#include <ostream>

#include <userver/utils/datetime.hpp>

#include <utils/schedule/split_days.hpp>

#include <utils/schedule/tests/utils.hpp>

// Чтобы красиво печатать параметры теста, неймспейс важен
namespace eats_restaurant_menu::utils::schedule {

[[maybe_unused]] std::ostream& operator<<(std::ostream& os,
                                          const Schedule& schedule) {
  os << "{week_day: " << schedule.week_day
     << ", from: " << schedule.from.count() << ", to: " << schedule.to.count()
     << "}";
  return os;
}

}  // namespace eats_restaurant_menu::utils::schedule

namespace eats_restaurant_menu::utils::schedule::tests {

namespace {

using namespace std::chrono_literals;

struct TestCase {
  std::string name;
  std::string from;
  std::string to;
  DaySchedules expected;
};

class SplitDayTest : public ::testing::TestWithParam<TestCase> {};

}  // namespace

TEST_P(SplitDayTest, SplitDay) {
  const auto params = GetParam();
  const auto from = ::utils::datetime::Stringtime(params.from);
  const auto to = ::utils::datetime::Stringtime(params.to);
  eats_places_availability::Schedule place_schedule{
      {from, to},
  };

  const auto result =
      SplitDays(place_schedule, ::utils::datetime::kDefaultTimezone);

  ASSERT_EQ(result, params.expected);
}

INSTANTIATE_TEST_SUITE_P(
    /**/, SplitDayTest,
    ::testing::Values(
        TestCase{
            "empty",
            "2022-06-15T10:00:00.0+0000",
            "2022-06-15T10:00:00.0+0000",
            {},
        },
        TestCase{
            "same_day",
            "2022-06-15T10:00:00.0+0000",
            "2022-06-15T12:00:00.0+0000",
            ToDaySchedule({
                Schedule{cctz::weekday::wednesday, 10h, 12h},
            }),
        },
        TestCase{
            "three_days",
            "2022-06-15T10:00:00.0+0000",
            "2022-06-17T12:00:00.0+0000",
            ToDaySchedule({
                Schedule{cctz::weekday::wednesday, 10h, 24h},
                Schedule{cctz::weekday::thursday, 0h, 24h},
                Schedule{cctz::weekday::friday, 0h, 12h},
            }),
        }),
    [](const auto& v) { return v.param.name; });

}  // namespace eats_restaurant_menu::utils::schedule::tests
