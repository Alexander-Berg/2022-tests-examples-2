#include <gtest/gtest.h>

#include <common/possible_income.hpp>

struct TestCalcIncomForEachHourParams {
  models::Chart tariffication_chart;
  std::array<double, common::impl::kHoursInDay> expected_result;
};

class TestCalcIncomeForEachHour
    : public testing::Test,
      public testing::WithParamInterface<TestCalcIncomForEachHourParams> {};

TEST_P(TestCalcIncomeForEachHour, Test) {
  const auto& p = GetParam();
  const auto result =
      common::impl::CalcIncomeForEachHour(p.tariffication_chart);
  ASSERT_EQ(p.expected_result, result);
}

INSTANTIATE_TEST_SUITE_P(
    PossibleIncome, TestCalcIncomeForEachHour,
    testing::Values(  //
        TestCalcIncomForEachHourParams{
            models::Chart{
                models::ChartColumn{0, 60.0},              // since 00:00
                models::ChartColumn{8 * 60, 120.0},        // since 8:00
                models::ChartColumn{8 * 60 + 20, 60.0},    // since 8:20
                models::ChartColumn{9 * 60, 180.0},        // since 9:00
                models::ChartColumn{9 * 60 + 30, 120.0},   // since 9:30
                models::ChartColumn{9 * 60 + 45, 180.0},   // since 9:45
                models::ChartColumn{11 * 60 + 30, 60.0},   // since 11:30
                models::ChartColumn{23 * 60 + 30, 120.0},  // since 23:30
            },
            {
                60.0,   // 00:00 -> 01:00
                60.0,   // 01:00 -> 02:00
                60.0,   // 02:00 -> 03:00
                60.0,   // 03:00 -> 04:00
                60.0,   // 04:00 -> 05:00
                60.0,   // 05:00 -> 06:00
                60.0,   // 06:00 -> 07:00
                60.0,   // 07:00 -> 08:00
                80.0,   // 08:00 -> 09:00
                165.0,  // 09:00 -> 10:00
                180.0,  // 10:00 -> 11:00
                120.0,  // 11:00 -> 12:00
                60.0,   // 12:00 -> 13:00
                60.0,   // 13:00 -> 14:00
                60.0,   // 14:00 -> 15:00
                60.0,   // 15:00 -> 16:00
                60.0,   // 16:00 -> 17:00
                60.0,   // 17:00 -> 18:00
                60.0,   // 18:00 -> 19:00
                60.0,   // 19:00 -> 20:00
                60.0,   // 20:00 -> 21:00
                60.0,   // 21:00 -> 22:00
                60.0,   // 22:00 -> 23:00
                90.0,   // 23:00 -> 00:00
            }},

        TestCalcIncomForEachHourParams{
            models::Chart{
                models::ChartColumn{0, 60.0},        // since 00:00
                models::ChartColumn{12 * 60, 30.0},  // since 12:00
            },
            {
                60.0,  // 00:00 -> 01:00
                60.0,  // 01:00 -> 02:00
                60.0,  // 02:00 -> 03:00
                60.0,  // 03:00 -> 04:00
                60.0,  // 04:00 -> 05:00
                60.0,  // 05:00 -> 06:00
                60.0,  // 06:00 -> 07:00
                60.0,  // 07:00 -> 08:00
                60.0,  // 08:00 -> 09:00
                60.0,  // 09:00 -> 10:00
                60.0,  // 10:00 -> 11:00
                60.0,  // 11:00 -> 12:00
                30.0,  // 12:00 -> 13:00
                30.0,  // 13:00 -> 14:00
                30.0,  // 14:00 -> 15:00
                30.0,  // 15:00 -> 16:00
                30.0,  // 16:00 -> 17:00
                30.0,  // 17:00 -> 18:00
                30.0,  // 18:00 -> 19:00
                30.0,  // 19:00 -> 20:00
                30.0,  // 20:00 -> 21:00
                30.0,  // 21:00 -> 22:00
                30.0,  // 22:00 -> 23:00
                30.0,  // 23:00 -> 00:00
            }}));
