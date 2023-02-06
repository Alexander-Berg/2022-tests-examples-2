#include <string>
#include <tuple>

#include <fmt/format.h>
#include <gmock/gmock.h>

#include <userver/utils/datetime.hpp>

#include "smart_rules/types/base_types.hpp"
#include "smart_rules/types/goal/window.hpp"

#include "builders.hpp"

using Window = billing_subventions_x::types::GoalWindow;

Window MakeWindow(int number, const std::string& start,
                  const std::string& end) {
  Window w;
  w.number = number;
  w.start = utils::datetime::Stringtime(start);
  w.end = utils::datetime::Stringtime(end);
  return w;
}

void AssertEqual(const Window& actual, const Window& expected) {
  ASSERT_THAT(actual.number, testing::Eq(expected.number));
  ASSERT_THAT(actual.start, testing::Eq(expected.start))
      << TimePointsNotEqual(actual.start, expected.start);
  ASSERT_THAT(actual.end, testing::Eq(expected.end))
      << TimePointsNotEqual(actual.end, expected.end);
}

class GoalWindowGeneratorTest
    : public testing::TestWithParam<std::tuple<std::string,  // starts_at
                                               int,          // window_size
                                               std::string,  // reference time
                                               std::string,  // timezone
                                               Window        // expected window
                                               >> {};

TEST_P(GoalWindowGeneratorTest, CalculatesWindowWithTimezone) {
  auto [starts_at, window, reference_time, timezone, expected] = GetParam();
  auto goal = GoalBuilder().WithStartsAt(starts_at).WithWindow(window).Build();
  AssertEqual(goal.CalcWindowForTimePoint(ATimePoint(reference_time), timezone),
              expected);
}

INSTANTIATE_TEST_SUITE_P(
    GoalWindowGeneratorTest, GoalWindowGeneratorTest,
    ::testing::Values(
        // reference_time == starts_at
        std::make_tuple("2021-09-01T00:00:00+0300", 1,
                        "2021-09-01T00:00:00+0300", "Europe/Moscow",
                        MakeWindow(1, "2021-09-01T00:00:00+0300",
                                   "2021-09-02T00:00:00+0300")),
        // before switch, zone without DST
        std::make_tuple("2021-09-01T00:00:00+0300", 1,
                        "2021-09-01T00:00:00+0300", "Europe/Moscow",
                        MakeWindow(1, "2021-09-01T00:00:00+0300",
                                   "2021-09-02T00:00:00+0300")),
        // switch to winter, zone without DST
        std::make_tuple("2021-09-01T00:00:00+0300", 1,
                        "2021-10-31T12:00:00+0300", "Europe/Moscow",
                        MakeWindow(61, "2021-10-31T00:00:00+0300",
                                   "2021-11-01T00:00:00+0300")),
        std::make_tuple("2021-09-01T00:00:00+0300", 28,
                        "2021-10-31T12:00:00+0300", "Europe/Moscow",
                        MakeWindow(3, "2021-10-27T00:00:00+0300",
                                   "2021-11-24T00:00:00+0300")),
        // somewhere in winter, zone without DST
        std::make_tuple("2021-09-01T00:00:00+0300", 28,
                        "2022-01-21T12:00:00+0300", "Europe/Moscow",
                        MakeWindow(6, "2022-01-19T00:00:00+0300",
                                   "2022-02-16T00:00:00+0300")),
        // switch to summer, zone without DST
        std::make_tuple("2021-09-01T00:00:00+0300", 1,
                        "2022-03-27T12:00:00+0300", "Europe/Moscow",
                        MakeWindow(208, "2022-03-27T00:00:00+0300",
                                   "2022-03-28T00:00:00+0300")),
        // after switch, zone without DST
        std::make_tuple("2021-09-01T00:00:00+0300", 1,
                        "2022-05-27T12:00:00+0300", "Europe/Moscow",
                        MakeWindow(269, "2022-05-27T00:00:00+0300",
                                   "2022-05-28T00:00:00+0300")),
        // before switch, zone with DST
        std::make_tuple("2021-09-01T00:00:00+0300", 1,
                        "2021-09-07T12:00:00+0300", "Europe/Tallinn",
                        MakeWindow(7, "2021-09-07T00:00:00+0300",
                                   "2021-09-08T00:00:00+0300")),
        // switch to winter, zone with DST
        std::make_tuple("2021-09-01T00:00:00+0300", 1,
                        "2021-10-31T12:00:00+0300", "Europe/Tallinn",
                        MakeWindow(61, "2021-10-31T00:00:00+0300",
                                   "2021-11-01T00:00:00+0200")),
        std::make_tuple("2021-09-01T00:00:00+0300", 1,
                        "2021-11-01T00:30:00+0200", "Europe/Tallinn",
                        MakeWindow(62, "2021-11-01T00:00:00+0200",
                                   "2021-11-02T00:00:00+0200")),
        std::make_tuple("2021-09-01T00:00:00+0300", 28,
                        "2021-10-31T12:00:00+0300", "Europe/Tallinn",
                        MakeWindow(3, "2021-10-27T00:00:00+0300",
                                   "2021-11-24T00:00:00+0200")),
        // somewhere in winter, zone with DST
        std::make_tuple("2021-09-01T00:00:00+0300", 28,
                        "2022-01-21T12:00:00+0300", "Europe/Tallinn",
                        MakeWindow(6, "2022-01-19T00:00:00+0200",
                                   "2022-02-16T00:00:00+0200")),
        // switch to summer, zone with DST
        std::make_tuple("2021-09-01T00:00:00+0300", 1,
                        "2022-03-27T12:00:00+0300", "Europe/Tallinn",
                        MakeWindow(208, "2022-03-27T00:00:00+0200",
                                   "2022-03-28T00:00:00+0300")),
        // after switch, zone with DST
        std::make_tuple("2021-09-01T00:00:00+0300", 1,
                        "2022-05-27T12:00:00+0300", "Europe/Tallinn",
                        MakeWindow(269, "2022-05-27T00:00:00+0300",
                                   "2022-05-28T00:00:00+0300"))

            ));
