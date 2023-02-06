#include "models/tariff_calc/helpers.hpp"

#include <tuple>

#include <gtest/gtest.h>

#include <models/tariffs.hpp>

using namespace tariff_calc;

TEST(TariffCalcHelpersSuitsTest, TestFromEqualsTo) {
  tariff::Category category;
  category.time_from = utils::datetime::timepair_t(0, 0);
  category.time_to = utils::datetime::timepair_t(0, 0);
  category.day_type = tariff::DayType::Everyday;
  EXPECT_TRUE(SuitsByTime(category, 0, 0, false));  // weird case
  EXPECT_FALSE(SuitsByTime(category, 0, 1, false));
  EXPECT_FALSE(SuitsByTime(category, 23, 59, false));
}

struct SuitsParamsAndResults {
  int hour;
  int minute;
  bool is_working_day;

  bool expected_workday_day;
  bool expected_workday_night;
  bool expected_holiday;
  bool expected_everyday_morning;
};

class TariffCalcHelpersSuitsTest
    : public ::testing::TestWithParam<SuitsParamsAndResults> {
  void SetUp() override {
    workday_day.time_from = utils::datetime::timepair_t(8, 0);
    workday_day.time_to = utils::datetime::timepair_t(17, 59);
    workday_day.day_type = tariff::DayType::Workday;

    workday_night.time_from = utils::datetime::timepair_t(18, 0);
    workday_night.time_to = utils::datetime::timepair_t(7, 59);
    workday_night.day_type = tariff::DayType::Workday;

    everyday_morning.time_from = utils::datetime::timepair_t(8, 0);
    everyday_morning.time_to = utils::datetime::timepair_t(17, 59);
    everyday_morning.day_type = tariff::DayType::Everyday;

    holiday.time_from = utils::datetime::timepair_t(0, 0);
    holiday.time_to = utils::datetime::timepair_t(23, 59);
    holiday.day_type = tariff::DayType::Dayoff;
  }

 protected:
  tariff::Category workday_day;
  tariff::Category workday_night;
  tariff::Category everyday_morning;
  tariff::Category holiday;
};

TEST_P(TariffCalcHelpersSuitsTest, TestSuitsByTimeWorkday) {
  const auto& args = GetParam();
  EXPECT_EQ(
      args.expected_workday_day,
      SuitsByTime(workday_day, args.hour, args.minute, args.is_working_day));
  EXPECT_EQ(
      args.expected_workday_night,
      SuitsByTime(workday_night, args.hour, args.minute, args.is_working_day));
  EXPECT_EQ(args.expected_everyday_morning,
            SuitsByTime(everyday_morning, args.hour, args.minute,
                        args.is_working_day));
  EXPECT_EQ(args.expected_holiday,
            SuitsByTime(holiday, args.hour, args.minute, args.is_working_day));
}

INSTANTIATE_TEST_CASE_P(
    TariffCalcHelpersSuitsAllValues, TariffCalcHelpersSuitsTest,
    ::testing::Values(
        SuitsParamsAndResults{6, 0, true, false, true, false, false},
        SuitsParamsAndResults{7, 59, true, false, true, false, false},
        SuitsParamsAndResults{8, 0, true, true, false, false, true},
        SuitsParamsAndResults{10, 0, true, true, false, false, true},
        SuitsParamsAndResults{17, 59, true, true, false, false, true},
        SuitsParamsAndResults{18, 0, true, false, true, false, false},
        SuitsParamsAndResults{23, 0, true, false, true, false, false},
        SuitsParamsAndResults{6, 0, false, false, false, true, false},
        SuitsParamsAndResults{8, 0, false, false, false, true, true},
        SuitsParamsAndResults{10, 0, false, false, false, true, true},
        SuitsParamsAndResults{17, 59, false, false, false, true, true},
        SuitsParamsAndResults{18, 0, false, false, false, true, false},
        SuitsParamsAndResults{23, 0, false, false, false, true, false}), );

TEST(TariffCalcHelpersSuitsByTypeTest, TestFromEqualsTo) {
  tariff::Category category;
  category.name = "econom";
  category.time_from = utils::datetime::timepair_t(0, 0);
  category.time_to = utils::datetime::timepair_t(0, 0);
  category.day_type = tariff::DayType::Everyday;
  category.category_type = tariff::CategoryType::Application;

  EXPECT_TRUE(SuitsByType(category, {"econom", "comfort"},
                          tariff::CategoryType::Application));
  EXPECT_TRUE(
      SuitsByType(category, {"comfort"}, tariff::CategoryType::Application));
  EXPECT_FALSE(SuitsByType(category, {"econom", "comfort"},
                           tariff::CategoryType::CallCenter));
  EXPECT_TRUE(
      SuitsByType(category, {"comfort"}, tariff::CategoryType::CallCenter));

  category.category_type = tariff::CategoryType::CallCenter;

  EXPECT_TRUE(SuitsByType(category, {"econom", "comfort"},
                          tariff::CategoryType::CallCenter));
  EXPECT_TRUE(
      SuitsByType(category, {"comfort"}, tariff::CategoryType::CallCenter));
  EXPECT_FALSE(SuitsByType(category, {"econom", "comfort"},
                           tariff::CategoryType::Application));
  EXPECT_FALSE(
      SuitsByType(category, {"comfort"}, tariff::CategoryType::Application));
}
