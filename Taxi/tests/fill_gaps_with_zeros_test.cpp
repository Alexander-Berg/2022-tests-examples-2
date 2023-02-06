#include <userver/utest/utest.hpp>

#include <utils/points_modifiers/fill_gaps_with_zeros.hpp>

#include "period_point.hpp"

namespace eats_report_storage::utils::points_modifiers {

namespace {

std::chrono::system_clock::time_point GetTimeFromString(
    const std::string& time_str) {
  return ::utils::datetime::Stringtime(
      time_str, ::utils::datetime::kDefaultTimezone, types::kDateFormat);
}

}  // namespace

struct FillGapsWithZerosData {
  types::PeriodPoints period_points;
  types::Period period;
  types::PeriodPoints expected;
};

class FillGapsWithZerosDataFull
    : public ::testing::TestWithParam<FillGapsWithZerosData> {};

const std::vector<FillGapsWithZerosData> kFillGapsWithZerosData{
    {{
         {1, std::nullopt, GetTimeFromString("2021-06-01"), {}, {}, {}},
         {1, std::nullopt, GetTimeFromString("2021-08-01"), {}, {}, {}},
     },
     {
         types::PeriodType::kCustom,
         types::GroupBy::kMonth,
         GetTimeFromString("2021-06-01"),
         GetTimeFromString("2021-09-03"),
     },
     {
         {1, std::nullopt, GetTimeFromString("2021-06-01"), {}, {}, {}},
         {0, std::nullopt, GetTimeFromString("2021-07-01"), {}, {}, {}},
         {1, std::nullopt, GetTimeFromString("2021-08-01"), {}, {}, {}},
         {0, std::nullopt, GetTimeFromString("2021-09-01"), {}, {}, {}},
     }},
    {{
         {1, std::nullopt, GetTimeFromString("2021-06-01"), {}, {}, {}},
         {1, std::nullopt, GetTimeFromString("2021-07-02"), {}, {}, {}},
         {1, std::nullopt, GetTimeFromString("2021-08-01"), {}, {}, {}},
     },
     {
         types::PeriodType::kCustom,
         types::GroupBy::kMonth,
         GetTimeFromString("2021-06-01"),
         GetTimeFromString("2021-09-03"),
     },
     {
         {1, std::nullopt, GetTimeFromString("2021-06-01"), {}, {}, {}},
         {0, std::nullopt, GetTimeFromString("2021-07-01"), {}, {}, {}},
         {1, std::nullopt, GetTimeFromString("2021-08-01"), {}, {}, {}},
         {0, std::nullopt, GetTimeFromString("2021-09-01"), {}, {}, {}},
     }},
    {{
         {1, std::nullopt, GetTimeFromString("2021-06-01"), {}, {}, {}},
         {1, std::nullopt, GetTimeFromString("2021-07-02"), {}, {}, {}},
         {1, std::nullopt, GetTimeFromString("2021-08-01"), {}, {}, {}},
     },
     {
         types::PeriodType::kCustom,
         types::GroupBy::kMonth,
         GetTimeFromString("2021-06-01"),
         GetTimeFromString("2021-09-03"),
     },
     {
         {1, std::nullopt, GetTimeFromString("2021-06-01"), {}, {}, {}},
         {0, std::nullopt, GetTimeFromString("2021-07-01"), {}, {}, {}},
         {1, std::nullopt, GetTimeFromString("2021-08-01"), {}, {}, {}},
         {0, std::nullopt, GetTimeFromString("2021-09-01"), {}, {}, {}},
     }},
    {{
         {1, std::nullopt, GetTimeFromString("2021-07-01"), {}, {}, {}},
         {1, std::nullopt, GetTimeFromString("2021-08-01"), {}, {}, {}},
     },
     {
         types::PeriodType::kCustom,
         types::GroupBy::kMonth,
         GetTimeFromString("2021-06-01"),
         GetTimeFromString("2021-09-03"),
     },
     {
         {0, std::nullopt, GetTimeFromString("2021-06-01"), {}, {}, {}},
         {1, std::nullopt, GetTimeFromString("2021-07-01"), {}, {}, {}},
         {1, std::nullopt, GetTimeFromString("2021-08-01"), {}, {}, {}},
         {0, std::nullopt, GetTimeFromString("2021-09-01"), {}, {}, {}},
     }},
    {{
         {1, std::nullopt, GetTimeFromString("2021-11-22"), {}, {}, {}},
         {1, std::nullopt, GetTimeFromString("2021-11-30"), {}, {}, {}},
         {2, std::nullopt, GetTimeFromString("2021-12-06"), {}, {}, {}},
     },
     {
         types::PeriodType::kCustom,
         types::GroupBy::kWeek,
         GetTimeFromString("2021-11-15"),
         GetTimeFromString("2021-12-12"),
     },
     {
         {0, std::nullopt, GetTimeFromString("2021-11-15"), {}, {}, {}},
         {1, std::nullopt, GetTimeFromString("2021-11-22"), {}, {}, {}},
         {0, std::nullopt, GetTimeFromString("2021-11-29"), {}, {}, {}},
         {2, std::nullopt, GetTimeFromString("2021-12-16"), {}, {}, {}},
     }},
    {{
         {1, std::nullopt, GetTimeFromString("2021-11-22"), {}, {}, {}},
         {1, std::nullopt, GetTimeFromString("2021-11-30"), {}, {}, {}},
         {2, std::nullopt, GetTimeFromString("2021-12-06"), {}, {}, {}},
     },
     {
         types::PeriodType::kCustom,
         types::GroupBy::kWeek,
         GetTimeFromString("2021-11-15"),
         GetTimeFromString("2021-12-13"),
     },
     {
         {0, std::nullopt, GetTimeFromString("2021-11-15"), {}, {}, {}},
         {1, std::nullopt, GetTimeFromString("2021-11-22"), {}, {}, {}},
         {0, std::nullopt, GetTimeFromString("2021-11-29"), {}, {}, {}},
         {2, std::nullopt, GetTimeFromString("2021-12-16"), {}, {}, {}},
     }},
    {{
         {1, std::nullopt, GetTimeFromString("2021-11-16"), {}, {}, {}},
         {2, std::nullopt, GetTimeFromString("2021-11-17"), {}, {}, {}},
         {3, std::nullopt, GetTimeFromString("2021-12-19"), {}, {}, {}},
         {4, std::nullopt, GetTimeFromString("2021-12-20"), {}, {}, {}},
     },
     {
         types::PeriodType::kCustom,
         types::GroupBy::kDay,
         GetTimeFromString("2021-11-15"),
         GetTimeFromString("2021-11-20"),
     },
     {
         {0, std::nullopt, GetTimeFromString("2021-11-15"), {}, {}, {}},
         {1, std::nullopt, GetTimeFromString("2021-11-16"), {}, {}, {}},
         {2, std::nullopt, GetTimeFromString("2021-11-17"), {}, {}, {}},
         {0, std::nullopt, GetTimeFromString("2021-11-18"), {}, {}, {}},
         {3, std::nullopt, GetTimeFromString("2021-11-19"), {}, {}, {}},
     }}};

INSTANTIATE_TEST_SUITE_P(FillGapsWithZerosData, FillGapsWithZerosDataFull,
                         ::testing::ValuesIn(kFillGapsWithZerosData));

TEST_P(FillGapsWithZerosDataFull, function_should_fill_gaps_with_zeros) {
  auto param = GetParam();
  FillGapsWithZeros()(param.period_points, param.period);
  ASSERT_EQ(param.period_points[1], param.expected[1]);
}

}  // namespace eats_report_storage::utils::points_modifiers
