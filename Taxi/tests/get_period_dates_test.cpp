#include <userver/utest/utest.hpp>

#include <utils/get_period_dates.hpp>

namespace eats_report_storage::types {

inline bool operator==(const Period& lhs, const Period& rhs) noexcept {
  return lhs.group_by == rhs.group_by && lhs.from == rhs.from &&
         lhs.to == rhs.to;
}

}  // namespace eats_report_storage::types

namespace eats_report_storage::utils {

struct GetStartNextGroupDateData {
  std::string time;
  types::GroupBy group_by;
  std::string expected_time;
};

class GetStartNextGroupDateFull
    : public ::testing::TestWithParam<GetStartNextGroupDateData> {};

const std::vector<GetStartNextGroupDateData> kGetStartNextGroupDateData{
    {"2021-07-27", types::GroupBy::kWeek, "2021-08-02"},
    {"2021-07-27", types::GroupBy::kMonth, "2021-08-01"},
    {"2021-07-27", types::GroupBy::kDay, "2021-07-28"},
    {"2021-07-27", types::GroupBy::kHour, "2021-07-28"}};

INSTANTIATE_TEST_SUITE_P(GetPeriodDates, GetStartNextGroupDateFull,
                         ::testing::ValuesIn(kGetStartNextGroupDateData));

TEST_P(GetStartNextGroupDateFull,
       function_should_return_start_next_group_period_date) {
  const auto& param = GetParam();
  std::chrono::system_clock::time_point time = ::utils::datetime::Stringtime(
      param.time, ::utils::datetime::kDefaultTimezone, types::kDateFormat);
  std::chrono::system_clock::time_point expected_time =
      ::utils::datetime::Stringtime(param.expected_time,
                                    ::utils::datetime::kDefaultTimezone,
                                    types::kDateFormat);
  ASSERT_EQ(GetStartNextGroupDate(param.group_by, time), expected_time);
}

struct GetStartCurrentGroupDateData {
  std::string time;
  types::GroupBy group_by;
  std::string expected_time;
};

class GetStartCurrentGroupDateFull
    : public ::testing::TestWithParam<GetStartCurrentGroupDateData> {};

const std::vector<GetStartCurrentGroupDateData> kGetStartCurrentGroupDate{
    {"2021-07-27", types::GroupBy::kWeek, "2021-07-26"},
    {"2021-07-27", types::GroupBy::kMonth, "2021-07-01"},
    {"2021-07-27", types::GroupBy::kDay, "2021-07-27"},
    {"2021-07-27", types::GroupBy::kHour, "2021-07-27"}};

INSTANTIATE_TEST_SUITE_P(GetPeriodDates, GetStartCurrentGroupDateFull,
                         ::testing::ValuesIn(kGetStartCurrentGroupDate));

TEST_P(GetStartCurrentGroupDateFull,
       function_should_return_start_current_group_period_date) {
  const auto& param = GetParam();
  std::chrono::system_clock::time_point time = ::utils::datetime::Stringtime(
      param.time, ::utils::datetime::kDefaultTimezone, types::kDateFormat);
  std::chrono::system_clock::time_point expected_time =
      ::utils::datetime::Stringtime(param.expected_time,
                                    ::utils::datetime::kDefaultTimezone,
                                    types::kDateFormat);
  ASSERT_EQ(GetStartCurrentGroupDate(param.group_by, time), expected_time);
}

struct GetPeriodDatesPeriodTypeData {
  std::string time;
  types::GroupBy group_by;
  types::PeriodType period_type;
  std::string expected_from;
  std::string expected_to;
};

class GetPeriodDatesPeriodTypeFull
    : public ::testing::TestWithParam<GetPeriodDatesPeriodTypeData> {};

const std::vector<GetPeriodDatesPeriodTypeData> kGetPeriodDatesPeriodType{
    {"2021-07-27", types::GroupBy::kHour, types::PeriodType::kYear,
     "2021-01-01", "2021-07-27"},
    {"2021-07-26", types::GroupBy::kDay, types::PeriodType::kWeek, "2021-07-19",
     "2021-07-26"},
    {"2021-07-27", types::GroupBy::kDay, types::PeriodType::kMonth,
     "2021-07-01", "2021-07-27"},
    {"2021-07-27", types::GroupBy::kWeek, types::PeriodType::kMonth,
     "2021-06-28", "2021-08-02"},
    {"2021-07-27", types::GroupBy::kMonth, types::PeriodType::kYear,
     "2021-01-01", "2021-08-01"}};

INSTANTIATE_TEST_SUITE_P(GetPeriodDates, GetPeriodDatesPeriodTypeFull,
                         ::testing::ValuesIn(kGetPeriodDatesPeriodType));

TEST_P(GetPeriodDatesPeriodTypeFull,
       function_should_return_period_for_group_period_argument) {
  const auto& param = GetParam();
  std::chrono::system_clock::time_point time = ::utils::datetime::Stringtime(
      param.time, ::utils::datetime::kDefaultTimezone, types::kDateFormat);
  std::chrono::system_clock::time_point expected_from =
      ::utils::datetime::Stringtime(param.expected_from,
                                    ::utils::datetime::kDefaultTimezone,
                                    types::kDateFormat);
  std::chrono::system_clock::time_point expected_to =
      ::utils::datetime::Stringtime(param.expected_to,
                                    ::utils::datetime::kDefaultTimezone,
                                    types::kDateFormat);
  ASSERT_EQ(GetPeriodDates(time, param.period_type, param.group_by),
            types::Period({param.period_type, param.group_by, expected_from,
                           expected_to}));
}

struct GetPeriodDatesFromToData {
  std::string from;
  std::string to;
  types::GroupBy group_by;
  std::string expected_from;
  std::string expected_to;
};

class GetPeriodDatesFromToFull
    : public ::testing::TestWithParam<GetPeriodDatesFromToData> {};

const std::vector<GetPeriodDatesFromToData> kGetPeriodDatesFromTo{
    {"2021-07-26", "2021-07-26", types::GroupBy::kHour, "2021-07-26",
     "2021-07-27"},
    {"2021-07-26", "2021-08-02", types::GroupBy::kHour, "2021-07-26",
     "2021-08-03"},
    {"2021-07-26", "2021-07-26", types::GroupBy::kDay, "2021-07-26",
     "2021-07-27"},
    {"2021-07-26", "2021-08-02", types::GroupBy::kDay, "2021-07-26",
     "2021-08-03"},
    {"2021-07-26", "2021-08-01", types::GroupBy::kWeek, "2021-07-26",
     "2021-08-02"},
    {"2021-07-27", "2021-08-03", types::GroupBy::kWeek, "2021-07-26",
     "2021-08-09"},
    {"2021-07-27", "2021-08-27", types::GroupBy::kMonth, "2021-07-01",
     "2021-09-01"},
    {"2021-01-01", "2021-07-31", types::GroupBy::kMonth, "2021-01-01",
     "2021-08-01"}};

INSTANTIATE_TEST_SUITE_P(GetPeriodDates, GetPeriodDatesFromToFull,
                         ::testing::ValuesIn(kGetPeriodDatesFromTo));

TEST_P(GetPeriodDatesFromToFull,
       function_should_return_period_for_from_and_to_arguments) {
  const auto& param = GetParam();
  std::chrono::system_clock::time_point from = ::utils::datetime::Stringtime(
      param.from, ::utils::datetime::kDefaultTimezone, types::kDateFormat);
  std::chrono::system_clock::time_point to = ::utils::datetime::Stringtime(
      param.to, ::utils::datetime::kDefaultTimezone, types::kDateFormat);
  std::chrono::system_clock::time_point expected_from =
      ::utils::datetime::Stringtime(param.expected_from,
                                    ::utils::datetime::kDefaultTimezone,
                                    types::kDateFormat);
  std::chrono::system_clock::time_point expected_to =
      ::utils::datetime::Stringtime(param.expected_to,
                                    ::utils::datetime::kDefaultTimezone,
                                    types::kDateFormat);
  ASSERT_EQ(GetPeriodDates(param.group_by, from, to),
            types::Period({types::PeriodType::kCustom, param.group_by,
                           expected_from, expected_to}));
}

struct GetPrevPeriodDatesTestData {
  std::string from;
  std::string to;
  types::GroupBy group_by;
  types::PeriodType period_type;
  std::string expected_from;
  std::string expected_to;
};

class GetPrevPeriodDatesTest
    : public ::testing::TestWithParam<GetPrevPeriodDatesTestData> {};

const std::vector<GetPrevPeriodDatesTestData> kGetPrevPeriodDatesTestData{
    {"2021-12-13", "2021-12-20", types::GroupBy::kDay, types::PeriodType::kWeek,
     "2021-12-06", "2021-12-13"},
    {"2021-12-13", "2021-12-17", types::GroupBy::kDay, types::PeriodType::kWeek,
     "2021-12-06", "2021-12-13"},
    {"2021-12-01", "2022-01-01", types::GroupBy::kDay,
     types::PeriodType::kMonth, "2021-11-01", "2021-12-01"},
    {"2021-12-01", "2021-12-17", types::GroupBy::kDay,
     types::PeriodType::kMonth, "2021-11-01", "2021-12-01"},
    {"2021-11-29", "2022-01-02", types::GroupBy::kWeek,
     types::PeriodType::kMonth, "2021-11-01", "2021-11-29"},
    {"2021-11-29", "2021-12-19", types::GroupBy::kWeek,
     types::PeriodType::kMonth, "2021-11-01", "2021-11-29"},
    {"2021-01-01", "2022-01-01", types::GroupBy::kDay, types::PeriodType::kYear,
     "2020-01-01", "2021-01-01"},
    {"2021-01-01", "2022-12-17", types::GroupBy::kDay, types::PeriodType::kYear,
     "2020-01-01", "2021-01-01"},
    {"2020-12-28", "2022-01-02", types::GroupBy::kWeek,
     types::PeriodType::kYear, "2019-12-30", "2020-12-28"},
    {"2020-12-28", "2022-12-19", types::GroupBy::kWeek,
     types::PeriodType::kYear, "2019-12-30", "2020-12-28"},
    {"2021-01-01", "2022-01-01", types::GroupBy::kMonth,
     types::PeriodType::kYear, "2020-01-01", "2021-01-01"},
    {"2021-01-01", "2021-12-01", types::GroupBy::kMonth,
     types::PeriodType::kYear, "2020-01-01", "2021-01-01"},
    {"2021-12-13", "2021-12-17", types::GroupBy::kDay,
     types::PeriodType::kCustom, "2021-12-09", "2021-12-13"},
    {"2021-11-29", "2021-12-19", types::GroupBy::kWeek,
     types::PeriodType::kCustom, "2021-11-08", "2021-11-29"},
    {"2021-01-01", "2021-12-01", types::GroupBy::kMonth,
     types::PeriodType::kCustom, "2020-02-01", "2021-01-01"}};

INSTANTIATE_TEST_SUITE_P(GetPeriodDates, GetPrevPeriodDatesTest,
                         ::testing::ValuesIn(kGetPrevPeriodDatesTestData));

TEST_P(GetPrevPeriodDatesTest, function_should_return_previous_period) {
  const auto& param = GetParam();
  std::chrono::system_clock::time_point from = ::utils::datetime::Stringtime(
      param.from, ::utils::datetime::kDefaultTimezone, types::kDateFormat);
  std::chrono::system_clock::time_point to = ::utils::datetime::Stringtime(
      param.to, ::utils::datetime::kDefaultTimezone, types::kDateFormat);
  types::Period input{param.period_type, param.group_by, from, to};

  std::chrono::system_clock::time_point expected_from =
      ::utils::datetime::Stringtime(param.expected_from,
                                    ::utils::datetime::kDefaultTimezone,
                                    types::kDateFormat);
  std::chrono::system_clock::time_point expected_to =
      ::utils::datetime::Stringtime(param.expected_to,
                                    ::utils::datetime::kDefaultTimezone,
                                    types::kDateFormat);
  types::Period expected{param.period_type, param.group_by, expected_from,
                         expected_to};

  ASSERT_EQ(GetPrevPeriodDates(input), expected);
}

}  // namespace eats_report_storage::utils
