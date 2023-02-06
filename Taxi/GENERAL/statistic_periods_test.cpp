#include "statistic_periods.hpp"
#include <gtest/gtest.h>
#include <iostream>
#include <userver/utils/datetime.hpp>

namespace eats_restapp_marketing::utils {
using namespace ::utils::datetime;

struct FetchChartPeriodTest
    : ::testing::TestWithParam<std::tuple<std::optional<Config>, GroupBy>> {};

struct NextSubPeriodTest
    : ::testing::TestWithParam<std::tuple<GroupBy, std::string>> {};

INSTANTIATE_TEST_SUITE_P(
    results, FetchChartPeriodTest,
    ::testing::Values(std::make_tuple(std::nullopt,
                                      GroupBy{Period::kDay, std::nullopt}),
                      // периоды больше 14 дней группировать по неделям, больше
                      // 45 - по месяцам
                      std::make_tuple(Config{14, 45, {}},
                                      GroupBy{Period::kWeek, std::nullopt}),
                      std::make_tuple(Config{14, 30, {}},
                                      GroupBy{Period::kMonth, std::nullopt}),
                      // инетрвал от 35 до 42 дней группировать по 14 дней
                      std::make_tuple(Config{14, 30, {{35, 42, 14}}},
                                      GroupBy{Period::kCustom,
                                              std::chrono::hours{14 * 24}})));

INSTANTIATE_TEST_SUITE_P(
    results, NextSubPeriodTest,
    ::testing::Values(
        std::make_tuple(GroupBy{Period::kDay, std::nullopt},
                        "2020-10-08T00:00:00.0+0000"),
        std::make_tuple(GroupBy{Period::kWeek, std::nullopt},
                        "2020-10-12T00:00:00.0+0000"),
        std::make_tuple(GroupBy{Period::kMonth, std::nullopt},
                        "2020-11-01T00:00:00.0+0000"),
        std::make_tuple(GroupBy{Period::kCustom, std::chrono::hours{14 * 24}},
                        "2020-10-21T00:00:00.0+0000"),
        std::make_tuple(GroupBy{Period::kCustom, std::chrono::hours{140 * 24}},
                        "2020-11-10T00:00:00.0+0000")));

TEST_P(FetchChartPeriodTest, FetchChartPeriod) {
  time_point from = Stringtime("2020-10-01T00:00:00.0+0000");
  time_point to = Stringtime("2020-11-10T00:00:00.0+0000");

  const auto [config, expected] = GetParam();

  auto group_by = FetchChartPeriod(from, to, config);
  ASSERT_EQ(group_by.period, expected.period);
  ASSERT_EQ(group_by.custom, expected.custom);
}

TEST_P(NextSubPeriodTest, NextSubPeriod) {
  time_point total_from = Stringtime("2020-10-07T00:00:00.0+0000");
  time_point total_to = Stringtime("2020-11-10T00:00:00.0+0000");

  const auto [group_by, expected_to] = GetParam();

  auto period = NextSubPeriod(std::nullopt, total_from, total_to, group_by);
  ASSERT_EQ(period.from, total_from);
  ASSERT_EQ(period.to, Stringtime(expected_to));
}

}  // namespace eats_restapp_marketing::utils
