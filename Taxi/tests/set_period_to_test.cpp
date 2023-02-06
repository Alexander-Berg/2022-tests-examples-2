#include <userver/utest/utest.hpp>
#include <userver/utils/mock_now.hpp>

#include <utils/points_modifiers/set_periods_to.hpp>

#include "period_point.hpp"

namespace eats_report_storage::utils::points_modifiers {

namespace {

std::chrono::system_clock::time_point GetTimeFromString(
    const std::string& time_str) {
  return ::utils::datetime::Stringtime(
      time_str, ::utils::datetime::kDefaultTimezone, types::kDateFormat);
}

}  // namespace

struct SetPeriodsToData {
  types::PeriodPoints period_points;
  types::Period period;
  types::PeriodPoints expected;
};

class SetPeriodsToDataFull : public ::testing::TestWithParam<SetPeriodsToData> {
};

const std::vector<SetPeriodsToData> kSetPeriodsToData{
    {{
         {1, std::nullopt, GetTimeFromString("2021-06-01"), {}, {}, {}},
         {1,
          handlers::MetricDataRowStatus::kPartlyActive,
          GetTimeFromString("2021-07-01"),
          {},
          {},
          {}},
         {1, std::nullopt, GetTimeFromString("2021-08-01"), {}, {}, {}},
     },
     {
         types::PeriodType::kCustom,
         types::GroupBy::kMonth,
         GetTimeFromString("2021-06-03"),
         GetTimeFromString("2021-08-03"),
     },
     {
         {1,
          std::nullopt,
          GetTimeFromString("2021-06-01"),
          GetTimeFromString("2021-06-30"),
          "01.06-30.06",
          {}},
         {1,
          handlers::MetricDataRowStatus::kPartlyActive,
          GetTimeFromString("2021-07-01"),
          GetTimeFromString("2021-07-31"),
          "01.07-31.07",
          {}},
         {1,
          std::nullopt,
          GetTimeFromString("2021-08-01"),
          GetTimeFromString("2021-08-02"),
          "01.08-02.08",
          {}},
     }},
    {{
         {1, std::nullopt, GetTimeFromString("2021-06-01"), {}, {}, {}},
         {1, std::nullopt, GetTimeFromString("2021-06-04"), {}, {}, {}},
     },
     {
         types::PeriodType::kCustom,
         types::GroupBy::kDay,
         GetTimeFromString("2021-06-03"),
         GetTimeFromString("2021-06-09"),
     },
     {
         {1,
          std::nullopt,
          GetTimeFromString("2021-06-01"),
          GetTimeFromString("2021-06-03"),
          "01.06-03.06",
          {}},
         {1,
          std::nullopt,
          GetTimeFromString("2021-06-04"),
          GetTimeFromString("2021-06-08"),
          "04.06-08.06",
          {}},
     }},
    {{
         {1,
          std::nullopt,
          GetTimeFromString("2021-06-01"),
          {},
          "something",
          {}},
     },
     {
         types::PeriodType::kCustom,
         types::GroupBy::kDay,
         GetTimeFromString("2021-06-03"),
         GetTimeFromString("2021-06-09"),
     },
     {
         {1,
          std::nullopt,
          GetTimeFromString("2021-06-01"),
          GetTimeFromString("2021-06-08"),
          "something",
          {}},
     }},
    {{
         {1, std::nullopt, GetTimeFromString("2021-06-03"), {}, {}, {}},
     },
     {
         types::PeriodType::kCustom,
         types::GroupBy::kDay,
         GetTimeFromString("2021-06-03"),
         GetTimeFromString("2021-06-04"),
     },
     {
         {1,
          std::nullopt,
          GetTimeFromString("2021-06-03"),
          GetTimeFromString("2021-06-03"),
          "03.06",
          {}},
     }},
    {{},
     {
         types::PeriodType::kCustom,
         types::GroupBy::kDay,
         GetTimeFromString("2021-06-03"),
         GetTimeFromString("2021-06-09"),
     },
     {}},
    {{
         {1, std::nullopt, GetTimeFromString("2021-09-01"), {}, {}, {}},
         {1, std::nullopt, GetTimeFromString("2021-10-01"), {}, {}, {}},
         {1, std::nullopt, GetTimeFromString("2021-11-01"), {}, {}, {}},
         {1, std::nullopt, GetTimeFromString("2021-12-01"), {}, {}, {}},
     },
     {
         types::PeriodType::kCustom,
         types::GroupBy::kMonth,
         GetTimeFromString("2021-09-03"),
         GetTimeFromString("2021-11-15"),
     },
     {
         {1,
          std::nullopt,
          GetTimeFromString("2021-09-01"),
          GetTimeFromString("2021-09-30"),
          "01.09-30.09",
          {}},
         {1,
          std::nullopt,
          GetTimeFromString("2021-10-01"),
          GetTimeFromString("2021-10-31"),
          "01.10-31.10",
          {}},
         {1,
          std::nullopt,
          GetTimeFromString("2021-11-01"),
          GetTimeFromString("2021-11-11"),
          "01.11-11.11",
          {}},
         {1,
          std::nullopt,
          GetTimeFromString("2021-12-01"),
          GetTimeFromString("2021-11-11"),
          "01.12",
          {}},
     }}};

INSTANTIATE_TEST_SUITE_P(SetPeriodsToData, SetPeriodsToDataFull,
                         ::testing::ValuesIn(kSetPeriodsToData));

TEST_P(SetPeriodsToDataFull, function_should_set_period_points_to) {
  ::utils::datetime::MockNowSet(GetTimeFromString("2021-11-11"));
  auto param = GetParam();
  SetPeriodsTo()(param.period_points, param.period);
  ASSERT_EQ(param.period_points, param.expected);
}

}  // namespace eats_report_storage::utils::points_modifiers
