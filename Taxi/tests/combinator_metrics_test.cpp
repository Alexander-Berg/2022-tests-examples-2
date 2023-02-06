#include <userver/utest/utest.hpp>

#include <types/time.hpp>
#include <utils/points_modifiers/combinator_metrics.hpp>

#include "period_point.hpp"

namespace eats_report_storage::utils::points_modifiers {

namespace {

std::chrono::system_clock::time_point GetTimeFromString(
    const std::string& time_str) {
  return ::utils::datetime::Stringtime(
      time_str, ::utils::datetime::kDefaultTimezone, types::kDateFormat);
}

}  // namespace

struct CombinatorMetricsSumData {
  types::PeriodPoints period_points;
  types::PeriodPoints expected;
};

class CombinatorMetricsSumFull
    : public ::testing::TestWithParam<CombinatorMetricsSumData> {};

const std::vector<CombinatorMetricsSumData> kCombinatorMetricsSumData{
    {{
         {1,
          std::nullopt,
          GetTimeFromString("2021-06-01"),
          GetTimeFromString("2021-09-01"),
          {},
          {}},
         {2,
          handlers::MetricDataRowStatus::kPartlyActive,
          GetTimeFromString("2021-06-01"),
          GetTimeFromString("2021-10-01"),
          {},
          {}},
         {3,
          handlers::MetricDataRowStatus::kActive,
          GetTimeFromString("2021-06-01"),
          {},
          {},
          {}},
         {11,
          handlers::MetricDataRowStatus::kActive,
          GetTimeFromString("2021-06-02"),
          {},
          {},
          {}},
         {12,
          handlers::MetricDataRowStatus::kActive,
          GetTimeFromString("2021-06-02"),
          {},
          {},
          {}},
         {13,
          handlers::MetricDataRowStatus::kActive,
          GetTimeFromString("2021-06-02"),
          {},
          {},
          {}},
         {21, std::nullopt, GetTimeFromString("2021-07-02"), {}, {}, {}},
     },
     {
         {6,
          handlers::MetricDataRowStatus::kPartlyActive,
          GetTimeFromString("2021-06-01"),
          GetTimeFromString("2021-09-01"),
          {},
          {}},
         {36,
          handlers::MetricDataRowStatus::kActive,
          GetTimeFromString("2021-06-02"),
          {},
          {},
          {}},
         {21, std::nullopt, GetTimeFromString("2021-07-02"), {}, {}, {}},
     }},
    {{
         {1, std::nullopt, GetTimeFromString("2021-06-01"), {}, {}, {}},
         {21, std::nullopt, GetTimeFromString("2021-07-02"), {}, {}, {}},
         {11,
          handlers::MetricDataRowStatus::kActive,
          GetTimeFromString("2021-06-02"),
          {},
          {},
          {}},
     },
     {
         {1, std::nullopt, GetTimeFromString("2021-06-01"), {}, {}, {}},
         {11,
          handlers::MetricDataRowStatus::kActive,
          GetTimeFromString("2021-06-02"),
          {},
          {},
          {}},
         {21, std::nullopt, GetTimeFromString("2021-07-02"), {}, {}, {}},
     }},
    {{
         {1, std::nullopt, GetTimeFromString("2021-06-01"), {}, {}, {}},
     },
     {
         {1, std::nullopt, GetTimeFromString("2021-06-01"), {}, {}, {}},
     }},
    {{}, {}},
};

INSTANTIATE_TEST_SUITE_P(CombinatorMetricsSumData, CombinatorMetricsSumFull,
                         ::testing::ValuesIn(kCombinatorMetricsSumData));

TEST_P(CombinatorMetricsSumFull, function_should_return_sum_metrics) {
  auto param = GetParam();
  SumCombinatorMetrics()(param.period_points, {});
  ASSERT_EQ(param.period_points, param.expected);
}

struct CombinatorMetricsAvgData {
  types::PeriodPoints period_points;
  types::PeriodPoints expected;
};

class CombinatorMetricsAvgFull
    : public ::testing::TestWithParam<CombinatorMetricsAvgData> {};

const std::vector<CombinatorMetricsAvgData> kCombinatorMetricsAvgData{
    {{
         {1,
          std::nullopt,
          GetTimeFromString("2021-06-01"),
          GetTimeFromString("2021-09-01"),
          {},
          {}},
         {2,
          handlers::MetricDataRowStatus::kPartlyActive,
          GetTimeFromString("2021-06-01"),
          GetTimeFromString("2021-10-01"),
          {},
          {}},
         {3,
          handlers::MetricDataRowStatus::kActive,
          GetTimeFromString("2021-06-01"),
          {},
          {},
          {}},
         {11,
          handlers::MetricDataRowStatus::kActive,
          GetTimeFromString("2021-06-02"),
          {},
          {},
          {}},
         {12,
          handlers::MetricDataRowStatus::kActive,
          GetTimeFromString("2021-06-02"),
          {},
          {},
          {}},
         {13,
          handlers::MetricDataRowStatus::kActive,
          GetTimeFromString("2021-06-02"),
          {},
          {},
          {}},
         {21, std::nullopt, GetTimeFromString("2021-07-02"), {}, {}, {}},
     },
     {
         {2,
          handlers::MetricDataRowStatus::kPartlyActive,
          GetTimeFromString("2021-06-01"),
          GetTimeFromString("2021-09-01"),
          {},
          3},
         {12,
          handlers::MetricDataRowStatus::kActive,
          GetTimeFromString("2021-06-02"),
          {},
          {},
          3},
         {21, std::nullopt, GetTimeFromString("2021-07-02"), {}, {}, 1},
     }},
    {{
         {1, std::nullopt, GetTimeFromString("2021-06-01"), {}, {}, {}},
         {21, std::nullopt, GetTimeFromString("2021-07-02"), {}, {}, {}},
         {11,
          handlers::MetricDataRowStatus::kActive,
          GetTimeFromString("2021-06-02"),
          {},
          {},
          {}},
     },
     {
         {1, std::nullopt, GetTimeFromString("2021-06-01"), {}, {}, 1},
         {11,
          handlers::MetricDataRowStatus::kActive,
          GetTimeFromString("2021-06-02"),
          {},
          {},
          1},
         {21, std::nullopt, GetTimeFromString("2021-07-02"), {}, {}, 1},
     }},
    {{
         {1, std::nullopt, GetTimeFromString("2021-06-01"), {}, {}, {}},
     },
     {
         {1, std::nullopt, GetTimeFromString("2021-06-01"), {}, {}, 1},
     }},
    {{}, {}},
};

INSTANTIATE_TEST_SUITE_P(CombinatorMetricsAvgData, CombinatorMetricsAvgFull,
                         ::testing::ValuesIn(kCombinatorMetricsAvgData));

TEST_P(CombinatorMetricsAvgFull, function_should_return_avg_metrics) {
  auto param = GetParam();
  AvgCombinatorMetrics()(param.period_points, {});
  ASSERT_EQ(param.period_points, param.expected);
}

struct CombinatorMetricsNotNullAvgData {
  types::PeriodPoints period_points;
  types::PeriodPoints expected;
};

class CombinatorMetricsNotNullAvgFull
    : public ::testing::TestWithParam<CombinatorMetricsNotNullAvgData> {};

const std::vector<CombinatorMetricsNotNullAvgData>
    kCombinatorMetricsNotNullAvgData{
        {{{1,
           std::nullopt,
           GetTimeFromString("2021-06-01"),
           GetTimeFromString("2021-09-01"),
           {},
           {}},
          {3,
           std::nullopt,
           GetTimeFromString("2021-06-01"),
           GetTimeFromString("2021-10-01"),
           {},
           {}},
          {0, std::nullopt, GetTimeFromString("2021-06-01"), {}, {}, {}}},
         {
             {2,
              std::nullopt,
              GetTimeFromString("2021-06-01"),
              GetTimeFromString("2021-09-01"),
              {},
              2},
         }},
        {{
             {0, std::nullopt, GetTimeFromString("2021-06-01"), {}, {}, {}},
         },
         {}}};

INSTANTIATE_TEST_SUITE_P(CombinatorMetricsNotNullAvgData,
                         CombinatorMetricsNotNullAvgFull,
                         ::testing::ValuesIn(kCombinatorMetricsNotNullAvgData));

TEST_P(CombinatorMetricsNotNullAvgFull,
       function_should_return_not_null_avg_metrics) {
  auto param = GetParam();
  NotNullAvgCombinatorMetrics()(param.period_points, {});
  ASSERT_EQ(param.period_points, param.expected);
}

}  // namespace eats_report_storage::utils::points_modifiers
