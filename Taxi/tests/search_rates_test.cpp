#include <gtest/gtest.h>

#include <chrono>
#include <vector>

#include <userver/utils/datetime.hpp>

#include <models/impl/search_rates.hpp>

using namespace std::chrono_literals;

using SearchControl = models::Subventions::SearchControl;
using Rate = models::impl::Rate;
using Rates = models::impl::Rates;
using WeekDay = clients::billing_subventions_x::WeekDay;
using Subventions = models::Subventions;

static const auto rates = Rates(
    {Rate{WeekDay::kTue, "10:00", "10.0"}, Rate{WeekDay::kTue, "20:00", "0.0"},
     Rate{WeekDay::kWed, "13:00", "42"}, Rate{WeekDay::kFri, "06:30", "0.001"},
     Rate{WeekDay::kSat, "10:00", "0"}});

TEST(SearchRatesForTimeInterval, SimpleMatches) {
  const auto interval_begin =
      utils::datetime::Stringtime("2021-03-23T17:00:00+0000");  // tuesday
  const auto interval_end =
      utils::datetime::Stringtime("2021-03-25T19:00:00+0000");  // thursday
  std::vector<Subventions::Rate> results;
  EXPECT_EQ(SearchControl::kContinue,
            models::impl::SearchRatesForTimeInterval(
                rates, interval_begin, interval_end, cctz::utc_time_zone(),
                [&results](const auto& rate) {
                  results.push_back(rate);
                  return SearchControl::kContinue;
                }));
  ASSERT_EQ(2, results.size());
  EXPECT_EQ(results[0], (Subventions::Rate{-7h, 10.0}));
  EXPECT_EQ(results[1], (Subventions::Rate{20h, 42.0}));
}

TEST(SearchRatesForTimeInterval, NextWeekShift) {
  const auto interval_begin =
      utils::datetime::Stringtime("2021-03-26T10:00:00+0000");  // friday
  const auto interval_end = utils::datetime::Stringtime(
      "2021-03-31T10:00:00+0000");  // next week wednesday
  std::vector<Subventions::Rate> results;
  EXPECT_EQ(SearchControl::kContinue,
            models::impl::SearchRatesForTimeInterval(
                rates, interval_begin, interval_end, cctz::utc_time_zone(),
                [&results](const auto& rate) {
                  results.push_back(rate);
                  return SearchControl::kContinue;
                }));
  ASSERT_EQ(2, results.size());
  EXPECT_EQ(results[0], (Subventions::Rate{4 * 24h, 10.0}));
  EXPECT_EQ(results[1], (Subventions::Rate{-3h - 30min, 0.001}));
}

TEST(SearchRatesForTimeInterval, CoveringInterval) {
  const auto interval_begin =
      utils::datetime::Stringtime("2021-03-22T10:00:00+0000");  // monday
  const auto interval_end = utils::datetime::Stringtime(
      "2021-04-01T10:00:00+0000");  // april fools' day
  std::vector<Subventions::Rate> results;
  EXPECT_EQ(SearchControl::kContinue,
            models::impl::SearchRatesForTimeInterval(
                rates, interval_begin, interval_end, cctz::utc_time_zone(),
                [&results](const auto& rate) {
                  results.push_back(rate);
                  return SearchControl::kContinue;
                }));
  ASSERT_EQ(3, results.size());
  EXPECT_EQ(results[0], (Subventions::Rate{24h, 10.0}));
  EXPECT_EQ(results[1], (Subventions::Rate{2 * 24h + 3h, 42.0}));
  EXPECT_EQ(results[2], (Subventions::Rate{4 * 24h - 3h - 30min, 0.001}));
}

TEST(SearchRatesForTimeInterval, NoMatches) {
  const auto interval_begin =
      utils::datetime::Stringtime("2021-03-23T21:00:00+0000");  // tuesday
  const auto interval_end =
      utils::datetime::Stringtime("2021-03-24T12:00:00+0000");  // wednesday
  std::vector<Subventions::Rate> results;
  EXPECT_EQ(SearchControl::kContinue,
            models::impl::SearchRatesForTimeInterval(
                rates, interval_begin, interval_end, cctz::utc_time_zone(),
                [&results](const auto& rate) {
                  results.push_back(rate);
                  return SearchControl::kContinue;
                }));
  ASSERT_EQ(0, results.size());
}

TEST(SearchRatesForTimeInterval, CustomTimezone) {
  const auto interval_begin =
      utils::datetime::Stringtime("2021-03-23T16:00:00+0000");  // tuesday
  const auto interval_end =
      utils::datetime::Stringtime("2021-03-25T19:00:00+0000");  // thursday
  const auto tz = cctz::fixed_time_zone(3h);                    // UTC+3
  std::vector<Subventions::Rate> results;
  EXPECT_EQ(SearchControl::kContinue, models::impl::SearchRatesForTimeInterval(
                                          rates, interval_begin, interval_end,
                                          tz, [&results](const auto& rate) {
                                            results.push_back(rate);
                                            return SearchControl::kContinue;
                                          }));
  ASSERT_EQ(2, results.size());
  EXPECT_EQ(results[0], (Subventions::Rate{-9h, 10.0}));
  EXPECT_EQ(results[1], (Subventions::Rate{18h, 42.0}));
}
