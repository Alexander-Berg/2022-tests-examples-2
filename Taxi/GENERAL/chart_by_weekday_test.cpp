#include <gtest/gtest.h>

#include "chart_by_weekday.hpp"

#include <utils/utils.hpp>

namespace {
namespace cbs = clients::billing_subventions;

const auto kRuleTimezone = utils::GetTimezone("Europe/Moscow");  // +03:00
const auto kAsiaKathmanduTimeZone =
    utils::GetTimezone("Asia/Kathmandu");  // +05:45
const auto kPacificPagoPagoTimeZone =
    utils::GetTimezone("Pacific/Pago_Pago");  // -11:00
const auto kAsiaVladivostokTimeZone =
    utils::GetTimezone("Asia/Vladivostok");  // +10:00

void AssertChartsEqual(const models::Chart& ref, const models::Chart& tst) {
  ASSERT_EQ(ref.size(), tst.size());
  for (size_t i = 0; i < ref.size(); ++i) {
    ASSERT_EQ(ref[i].minutes, tst[i].minutes);
    ASSERT_EQ(ref[i].rate_per_hour, tst[i].rate_per_hour);
  }
}

void CheckCharts(const std::vector<models::Chart>& ref,
                 const std::vector<models::Chart>& tst) {
  ASSERT_EQ(ref.size(), tst.size());
  for (size_t i = 0; i < ref.size(); ++i) {
    AssertChartsEqual(ref[i], tst[i]);
  }
}

class SharingValueBetweenDaysTestData
    : public testing::Test,
      public testing::WithParamInterface<
          std::tuple<cctz::time_zone, std::vector<models::Chart>>> {};

class OneTimePointTestData
    : public testing::Test,
      public testing::WithParamInterface<
          std::tuple<cctz::time_zone, std::vector<models::Chart>>> {};

class ManyIntervalsTestData
    : public testing::Test,
      public testing::WithParamInterface<
          std::tuple<cctz::time_zone, std::vector<models::Chart>>> {};

}  // namespace

TEST_P(SharingValueBetweenDaysTestData, SharingValueBetweenDays) {
  const auto& [client_timezone, ref] = GetParam();
  const std::vector<cbs::RateValue> rates{
      {cbs::RateValueWeekday::kMon, "05:00", "2.0"},
      {cbs::RateValueWeekday::kSun, "12:00", "7.0"}};

  const std::vector<models::Chart> tst = models::BuildChartsByWeekdays(
      rates, 0.0f, kRuleTimezone, client_timezone);

  CheckCharts(ref, tst);
}

INSTANTIATE_TEST_SUITE_P(
    ChartByWeekday, SharingValueBetweenDaysTestData,
    testing::Values(
        std::make_tuple(
            kRuleTimezone,
            std::vector<models::Chart>{
                models::Chart{{0, 7 * 60}, {5 * 60, 2 * 60}},
                models::Chart{{0, 2 * 60}}, models::Chart{{0, 2 * 60}},
                models::Chart{{0, 2 * 60}}, models::Chart{{0, 2 * 60}},
                models::Chart{{0, 2 * 60}},
                models::Chart{{0, 2 * 60}, {12 * 60, 7 * 60}}}),
        std::make_tuple(
            kAsiaKathmanduTimeZone,
            std::vector<models::Chart>{
                models::Chart{{0, 7 * 60}, {7 * 60 + 45, 2 * 60}},
                models::Chart{{0, 2 * 60}}, models::Chart{{0, 2 * 60}},
                models::Chart{{0, 2 * 60}}, models::Chart{{0, 2 * 60}},
                models::Chart{{0, 2 * 60}},
                models::Chart{{0, 2 * 60}, {14 * 60 + 45, 7 * 60}}}),
        std::make_tuple(
            kPacificPagoPagoTimeZone,
            std::vector<models::Chart>{
                models::Chart{{0, 2 * 60}}, models::Chart{{0, 2 * 60}},
                models::Chart{{0, 2 * 60}}, models::Chart{{0, 2 * 60}},
                models::Chart{{0, 2 * 60}},
                models::Chart{{0, 2 * 60}, {22 * 60, 7 * 60}},
                models::Chart{{0, 7 * 60}, {15 * 60, 2 * 60}}}),
        std::make_tuple(
            kAsiaVladivostokTimeZone,
            std::vector<models::Chart>{
                models::Chart{{0, 7 * 60}, {12 * 60, 2 * 60}},
                models::Chart{{0, 2 * 60}}, models::Chart{{0, 2 * 60}},
                models::Chart{{0, 2 * 60}}, models::Chart{{0, 2 * 60}},
                models::Chart{{0, 2 * 60}},
                models::Chart{{0, 2 * 60}, {19 * 60, 7 * 60}}})));

TEST_P(OneTimePointTestData, OneTimepoint) {
  const auto& [client_timezone, ref] = GetParam();
  const std::vector<cbs::RateValue> rates{
      {cbs::RateValueWeekday::kMon, "05:00", "2.0"}};

  const std::vector<models::Chart> tst = models::BuildChartsByWeekdays(
      rates, 0.0f, kRuleTimezone, client_timezone);

  CheckCharts(ref, tst);
}

INSTANTIATE_TEST_SUITE_P(
    ChartByWeekday, OneTimePointTestData,
    testing::Values(
        std::make_tuple(
            kRuleTimezone,
            std::vector<models::Chart>{
                models::Chart{{0, 2 * 60}, {5 * 60, 2 * 60}},
                models::Chart{{0, 2 * 60}}, models::Chart{{0, 2 * 60}},
                models::Chart{{0, 2 * 60}}, models::Chart{{0, 2 * 60}},
                models::Chart{{0, 2 * 60}}, models::Chart{{0, 2 * 60}}}),
        std::make_tuple(
            kAsiaKathmanduTimeZone,
            std::vector<models::Chart>{
                models::Chart{{0, 2 * 60}, {7 * 60 + 45, 2 * 60}},
                models::Chart{{0, 2 * 60}}, models::Chart{{0, 2 * 60}},
                models::Chart{{0, 2 * 60}}, models::Chart{{0, 2 * 60}},
                models::Chart{{0, 2 * 60}}, models::Chart{{0, 2 * 60}}}),
        std::make_tuple(
            kPacificPagoPagoTimeZone,
            std::vector<models::Chart>{
                models::Chart{{0, 2 * 60}}, models::Chart{{0, 2 * 60}},
                models::Chart{{0, 2 * 60}}, models::Chart{{0, 2 * 60}},
                models::Chart{{0, 2 * 60}}, models::Chart{{0, 2 * 60}},
                models::Chart{{0, 2 * 60}, {15 * 60, 2 * 60}}}),
        std::make_tuple(
            kAsiaVladivostokTimeZone,
            std::vector<models::Chart>{
                models::Chart{{0, 2 * 60}, {12 * 60, 2 * 60}},
                models::Chart{{0, 2 * 60}}, models::Chart{{0, 2 * 60}},
                models::Chart{{0, 2 * 60}}, models::Chart{{0, 2 * 60}},
                models::Chart{{0, 2 * 60}}, models::Chart{{0, 2 * 60}}})));

TEST_P(ManyIntervalsTestData, ManyIntervals) {
  const auto& [client_timezone, ref] = GetParam();
  const std::vector<cbs::RateValue> rates{
      {cbs::RateValueWeekday::kMon, "05:00", "2.0"},
      {cbs::RateValueWeekday::kMon, "03:00", "1.0"},
      {cbs::RateValueWeekday::kMon, "10:00", "3.0"},
      {cbs::RateValueWeekday::kMon, "23:00", "5.0"},
      {cbs::RateValueWeekday::kMon, "18:00", "4.0"}};
  const std::vector<models::Chart> tst = models::BuildChartsByWeekdays(
      rates, 0.0f, kRuleTimezone, client_timezone);

  CheckCharts(ref, tst);
}

INSTANTIATE_TEST_SUITE_P(
    ChartByWeekday, ManyIntervalsTestData,
    testing::Values(
        std::make_tuple(
            kRuleTimezone,
            std::vector<models::Chart>{
                models::Chart{{0, 5 * 60},
                              {3 * 60, 1 * 60},
                              {5 * 60, 2 * 60},
                              {10 * 60, 3 * 60},
                              {18 * 60, 4 * 60},
                              {23 * 60, 5 * 60}},
                models::Chart{{0, 5 * 60}}, models::Chart{{0, 5 * 60}},
                models::Chart{{0, 5 * 60}}, models::Chart{{0, 5 * 60}},
                models::Chart{{0, 5 * 60}}, models::Chart{{0, 5 * 60}}}),
        std::make_tuple(
            kAsiaKathmanduTimeZone,
            std::vector<models::Chart>{
                models::Chart{{0, 5 * 60},
                              {5 * 60 + 45, 1 * 60},
                              {7 * 60 + 45, 2 * 60},
                              {12 * 60 + 45, 3 * 60},
                              {20 * 60 + 45, 4 * 60}},
                models::Chart{{0, 4 * 60}, {1 * 60 + 45, 5 * 60}},
                models::Chart{{0, 5 * 60}}, models::Chart{{0, 5 * 60}},
                models::Chart{{0, 5 * 60}}, models::Chart{{0, 5 * 60}},
                models::Chart{{0, 5 * 60}}}),
        std::make_tuple(
            kPacificPagoPagoTimeZone,
            std::vector<models::Chart>{
                models::Chart{

                    {0, 3 * 60}, {4 * 60, 4 * 60}, {9 * 60, 5 * 60}},
                models::Chart{{0, 5 * 60}}, models::Chart{{0, 5 * 60}},
                models::Chart{{0, 5 * 60}}, models::Chart{{0, 5 * 60}},
                models::Chart{{0, 5 * 60}},
                models::Chart{{0, 5 * 60},
                              {13 * 60, 1 * 60},
                              {15 * 60, 2 * 60},
                              {20 * 60, 3 * 60}}}),
        std::make_tuple(
            kAsiaVladivostokTimeZone,
            std::vector<models::Chart>{
                models::Chart{{0, 5 * 60},
                              {10 * 60, 1 * 60},
                              {12 * 60, 2 * 60},
                              {17 * 60, 3 * 60}},
                models::Chart{{0, 3 * 60}, {1 * 60, 4 * 60}, {6 * 60, 5 * 60}},
                models::Chart{{0, 5 * 60}}, models::Chart{{0, 5 * 60}},
                models::Chart{{0, 5 * 60}}, models::Chart{{0, 5 * 60}},
                models::Chart{{0, 5 * 60}}})));
