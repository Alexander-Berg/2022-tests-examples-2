#include <models/select_discount_params.hpp>

#include <chrono>

#include <gtest/gtest.h>

#include <userver/formats/json.hpp>
#include <userver/utils/boost_uuid4.hpp>

namespace {

using namespace models;
using namespace std::chrono_literals;

const auto kDiscountGroupId = utils::generators::GenerateBoostUuid();
const std::string kUtc = "UTC";
const std::string kMoscowTimezone = "Europe/Moscow";
using TimePoint = std::chrono::system_clock::time_point;
using DiscountUsages = discounts::models::DiscountUsages;
using Usage = DiscountUsages::Usage;

TimePoint GetTimePoint(const std::string& time) {
  return formats::json::FromString(
             fmt::format(R"JSON({{"value": "{0}"  }})JSON", time))["value"]
      .As<TimePoint>();
}

}  // namespace

/*
Test scheme:
  case №                         3,4            2             1    6,5
  budget                       450,550         180           180 700,2000
                                  |             |             |     |
  usage      200          400     V     300     V     200     V     X
  time   -----+------------+------+------+------+------+------+-----X----->
  diff_time  -4h          -3h   -2.5h   -2h  -1.5h    -1h   -0.5h
*/
TEST(SelectDiscountParams, MatchByBudget) {
  DiscountUsages usages;
  auto tp = GetTimePoint("2020-01-01T12:00:00+00:00");
  usages.Add(boost::uuids::uuid{kDiscountGroupId},
             {{GetTimePoint("2020-01-01T08:00:00+00:00"), 200.},
              {GetTimePoint("2020-01-01T09:00:00+00:00"), 400.},
              {GetTimePoint("2020-01-01T10:00:00+00:00"), 300.},
              {GetTimePoint("2020-01-01T11:00:00+00:00"), 200.}});
  discounts::models::LazyData<DiscountUsages> lazy_data{
      [&usages]() -> std::optional<DiscountUsages> { return usages; }};
  // Case 1
  auto rule = std::vector<handlers::MaximumBudgetPerPerson>{
      {{180,
        handlers::Interval{handlers::IntervalType::kLastSeconds, 30 * 60}}}};
  EXPECT_TRUE(SelectDiscountParams::MatchByBudget(kDiscountGroupId, rule,
                                                  lazy_data, tp, kUtc));
  // Case 2
  rule = std::vector<handlers::MaximumBudgetPerPerson>{
      {{180,
        handlers::Interval{handlers::IntervalType::kLastSeconds, 90 * 60}}}};
  EXPECT_FALSE(SelectDiscountParams::MatchByBudget(kDiscountGroupId, rule,
                                                   lazy_data, tp, kUtc));
  // Case 3
  rule = std::vector<handlers::MaximumBudgetPerPerson>{
      {{550,
        handlers::Interval{handlers::IntervalType::kLastSeconds, 150 * 60}}}};
  EXPECT_TRUE(SelectDiscountParams::MatchByBudget(kDiscountGroupId, rule,
                                                  lazy_data, tp, kUtc));
  // Case 4
  rule = std::vector<handlers::MaximumBudgetPerPerson>{
      {{450,
        handlers::Interval{handlers::IntervalType::kLastSeconds, 150 * 60}}}};
  EXPECT_FALSE(SelectDiscountParams::MatchByBudget(kDiscountGroupId, rule,
                                                   lazy_data, tp, kUtc));
  // Case 5
  rule = std::vector<handlers::MaximumBudgetPerPerson>{{2000}};
  EXPECT_TRUE(SelectDiscountParams::MatchByBudget(kDiscountGroupId, rule,
                                                  lazy_data, tp, kUtc));
  // Case 6
  rule = std::vector<handlers::MaximumBudgetPerPerson>{{700}};
  EXPECT_FALSE(SelectDiscountParams::MatchByBudget(kDiscountGroupId, rule,
                                                   lazy_data, tp, kUtc));
}

TEST(SelectDiscountParams, MatchByDiscountUsages__WithoutDiscountUsages) {
  const TimePoint tp{10h};
  DiscountUsages usages;
  discounts::models::LazyData<DiscountUsages> lazy_data{
      []() -> std::optional<DiscountUsages> { return std::nullopt; }};
  std::vector<handlers::DiscountUsageRestriction> discount_usage_restrictions =
      {{10, std::nullopt}};
  EXPECT_FALSE(SelectDiscountParams::MatchDiscountRule(
      kDiscountGroupId, discount_usage_restrictions, lazy_data, tp, kUtc));
}

TEST(SelectDiscountParams, MatchByDiscountUsages__WithoutInterval) {
  const TimePoint tp{10h};
  DiscountUsages usages;
  usages.Add(boost::uuids::uuid{kDiscountGroupId},
             {tp, tp - 1h, tp - 2h, tp - 3h, tp - 4h});

  discounts::models::LazyData<DiscountUsages> lazy_data{
      [&usages]() -> std::optional<DiscountUsages> { return usages; }};
  std::vector<handlers::DiscountUsageRestriction> discount_usage_restrictions =
      {{5, std::nullopt}};
  EXPECT_FALSE(SelectDiscountParams::MatchDiscountRule(
      kDiscountGroupId, discount_usage_restrictions, lazy_data, tp, kUtc));

  discount_usage_restrictions = {{6, std::nullopt}};
  EXPECT_TRUE(SelectDiscountParams::MatchDiscountRule(
      kDiscountGroupId, discount_usage_restrictions, lazy_data, tp, kUtc));
}

TEST(SelectDiscountParams, MatchByDiscountUsages__WithSecondsInterval) {
  TimePoint tp{10s};
  DiscountUsages usages;
  usages.Add(boost::uuids::uuid{kDiscountGroupId}, {tp - 1ms});

  discounts::models::LazyData<DiscountUsages> lazy_data{
      [&usages]() -> std::optional<DiscountUsages> { return usages; }};
  auto discount_usage_restrictions =
      std::vector<handlers::DiscountUsageRestriction>{
          {{1, handlers::Interval{handlers::IntervalType::kLastSeconds, 1}}}};
  EXPECT_FALSE(SelectDiscountParams::MatchDiscountRule(
      kDiscountGroupId, discount_usage_restrictions, lazy_data, tp, kUtc));
  tp += 1s;
  EXPECT_TRUE(SelectDiscountParams::MatchDiscountRule(
      kDiscountGroupId, discount_usage_restrictions, lazy_data, tp, kUtc));
}

TEST(SelectDiscountParams, MatchByDiscountUsages__WithHoursInterval) {
  auto tp = GetTimePoint("2020-01-01T09:05:00+00:00");
  DiscountUsages usages;
  usages.Add(boost::uuids::uuid{kDiscountGroupId},
             {{GetTimePoint("2020-01-01T08:01:00+00:00"), 0.}});

  discounts::models::LazyData<DiscountUsages> lazy_data{
      [&usages]() -> std::optional<DiscountUsages> { return usages; }};
  auto discount_usage_restrictions =
      std::vector<handlers::DiscountUsageRestriction>{
          {{1, handlers::Interval{handlers::IntervalType::kLastHours, 2}}}};
  EXPECT_FALSE(SelectDiscountParams::MatchDiscountRule(
      kDiscountGroupId, discount_usage_restrictions, lazy_data, tp, kUtc));
  tp = GetTimePoint("2020-01-01T10:00:00+00:00");
  EXPECT_TRUE(SelectDiscountParams::MatchDiscountRule(
      kDiscountGroupId, discount_usage_restrictions, lazy_data, tp, kUtc));
}

TEST(SelectDiscountParams, MatchByDiscountUsages__WithDaysIntervalInUTC) {
  auto tp = GetTimePoint("2020-01-02T09:30:00+00:00");
  DiscountUsages usages;
  usages.Add(boost::uuids::uuid{kDiscountGroupId},
             {{GetTimePoint("2020-01-01T08:01:00+00:00"), 0.}});

  discounts::models::LazyData<DiscountUsages> lazy_data{
      [&usages]() -> std::optional<DiscountUsages> { return usages; }};
  auto discount_usage_restrictions =
      std::vector<handlers::DiscountUsageRestriction>{
          {{1, handlers::Interval{handlers::IntervalType::kLastDays, 2}}}};
  EXPECT_FALSE(SelectDiscountParams::MatchDiscountRule(
      kDiscountGroupId, discount_usage_restrictions, lazy_data, tp, kUtc));
  tp = GetTimePoint("2020-01-02T23:59:00+00:00");
  EXPECT_FALSE(SelectDiscountParams::MatchDiscountRule(
      kDiscountGroupId, discount_usage_restrictions, lazy_data, tp, kUtc));
  tp = GetTimePoint("2020-01-03T00:00:00+00:00");
  EXPECT_TRUE(SelectDiscountParams::MatchDiscountRule(
      kDiscountGroupId, discount_usage_restrictions, lazy_data, tp, kUtc));
}

TEST(SelectDiscountParams,
     MatchByDiscountUsages__WithDaysIntervalInMoscowTimezone) {
  auto tp = GetTimePoint("2020-01-02T09:30:00+00:00");
  DiscountUsages usages;
  usages.Add(boost::uuids::uuid{kDiscountGroupId},
             {{GetTimePoint("2020-01-01T08:01:00+00:00"), 0.}});

  discounts::models::LazyData<DiscountUsages> lazy_data{
      [&usages]() -> std::optional<DiscountUsages> { return usages; }};
  auto discount_usage_restrictions =
      std::vector<handlers::DiscountUsageRestriction>{
          {{1, handlers::Interval{handlers::IntervalType::kLastDays, 2}}}};
  EXPECT_FALSE(SelectDiscountParams::MatchDiscountRule(
      kDiscountGroupId, discount_usage_restrictions, lazy_data, tp,
      kMoscowTimezone));
  tp = GetTimePoint("2020-01-03T00:00:00+03:00") - 1s;
  EXPECT_FALSE(SelectDiscountParams::MatchDiscountRule(
      kDiscountGroupId, discount_usage_restrictions, lazy_data, tp,
      kMoscowTimezone));
  tp = GetTimePoint("2020-01-03T00:00:00+03:00");
  EXPECT_TRUE(SelectDiscountParams::MatchDiscountRule(
      kDiscountGroupId, discount_usage_restrictions, lazy_data, tp,
      kMoscowTimezone));
}

TEST(SelectDiscountParams, MatchByDiscountUsages__WithWeeksInterval) {
  auto tp = GetTimePoint("2020-01-02T09:30:00+00:00");
  DiscountUsages usages;
  usages.Add(boost::uuids::uuid{kDiscountGroupId},
             {{GetTimePoint("2020-01-01T08:01:00+00:00"), 0.}});

  discounts::models::LazyData<DiscountUsages> lazy_data{
      [&usages]() -> std::optional<DiscountUsages> { return usages; }};
  auto discount_usage_restrictions =
      std::vector<handlers::DiscountUsageRestriction>{
          {{1, handlers::Interval{handlers::IntervalType::kLastWeeks, 2}}}};
  EXPECT_FALSE(SelectDiscountParams::MatchDiscountRule(
      kDiscountGroupId, discount_usage_restrictions, lazy_data, tp, kUtc));
  tp = GetTimePoint("2020-01-13T00:00:00+00:00") - 1s;
  EXPECT_FALSE(SelectDiscountParams::MatchDiscountRule(
      kDiscountGroupId, discount_usage_restrictions, lazy_data, tp, kUtc));
  tp = GetTimePoint("2020-01-13T00:00:00+00:00");
  EXPECT_TRUE(SelectDiscountParams::MatchDiscountRule(
      kDiscountGroupId, discount_usage_restrictions, lazy_data, tp, kUtc));
}

TEST(SelectDiscountParams, MatchByDiscountUsages__WithMonthsIntervalInOneYear) {
  auto tp = GetTimePoint("2020-04-25T00:00:00+00:00");
  DiscountUsages usages;
  usages.Add(boost::uuids::uuid{kDiscountGroupId},
             {{GetTimePoint("2020-04-15T08:01:00+00:00"), 0.}});

  discounts::models::LazyData<DiscountUsages> lazy_data{
      [&usages]() -> std::optional<DiscountUsages> { return usages; }};
  auto discount_usage_restrictions =
      std::vector<handlers::DiscountUsageRestriction>{
          {{1, handlers::Interval{handlers::IntervalType::kLastMonthes, 2}}}};
  EXPECT_FALSE(SelectDiscountParams::MatchDiscountRule(
      kDiscountGroupId, discount_usage_restrictions, lazy_data, tp, kUtc));
  tp = GetTimePoint("2020-06-01T00:00:00+00:00") - 1s;
  EXPECT_FALSE(SelectDiscountParams::MatchDiscountRule(
      kDiscountGroupId, discount_usage_restrictions, lazy_data, tp, kUtc));
  tp = GetTimePoint("2020-06-01T00:00:00+00:00");
  EXPECT_TRUE(SelectDiscountParams::MatchDiscountRule(
      kDiscountGroupId, discount_usage_restrictions, lazy_data, tp, kUtc));
}

TEST(SelectDiscountParams,
     MatchByDiscountUsages__WithMonthsIntervalInDifferentYear) {
  auto tp = GetTimePoint("2021-01-25T00:00:00+00:00");
  DiscountUsages usages;
  usages.Add(boost::uuids::uuid{kDiscountGroupId},
             {{GetTimePoint("2020-12-15T08:01:00+00:00"), 0.}});

  discounts::models::LazyData<DiscountUsages> lazy_data{
      [&usages]() -> std::optional<DiscountUsages> { return usages; }};
  auto discount_usage_restrictions =
      std::vector<handlers::DiscountUsageRestriction>{
          {{1, handlers::Interval{handlers::IntervalType::kLastMonthes, 2}}}};
  EXPECT_FALSE(SelectDiscountParams::MatchDiscountRule(
      kDiscountGroupId, discount_usage_restrictions, lazy_data, tp, kUtc));
  tp = GetTimePoint("2021-02-01T00:00:00+00:00") - 1s;
  EXPECT_FALSE(SelectDiscountParams::MatchDiscountRule(
      kDiscountGroupId, discount_usage_restrictions, lazy_data, tp, kUtc));
  tp = GetTimePoint("2021-02-01T00:00:00+00:00");
  EXPECT_TRUE(SelectDiscountParams::MatchDiscountRule(
      kDiscountGroupId, discount_usage_restrictions, lazy_data, tp, kUtc));
}

TEST(SelectDiscountParams, MatchBySchedule) {
  auto rule = formats::json::FromString(R"JSON(
{
    "description": "test",
    "discount_meta": {},
    "name": "team_test_2",
    "values_with_schedules": [
        {
            "money_value": {
                "discount_value": {
                    "value": {
                        "hyperbola_lower": {
                            "a": 0,
                            "c": 1,
                            "p": 5
                        },
                        "hyperbola_upper": {
                            "a": 0,
                            "c": 1,
                            "p": 5
                        },
                        "threshold": 1000
                    },
                    "value_type": "hyperbolas"
                },
                "max_absolute_value": 5
            },
            "schedule": {
                "intervals": [
                    {
                        "day": [
                            1,
                            2,
                            3,
                            4,
                            5,
                            6,
                            7
                        ],
                        "exclude": false
                    },
                    {
                        "daytime": [
                            {
                              "from": "17:00:00",
                              "to": "23:59:59"
                            }
                        ],
                        "exclude": false
                    }
                ],
                "timezone": "LOCAL"
            }
        }
    ]
}
)JSON")
                  .As<handlers::Rule>();
  EXPECT_FALSE(SelectDiscountParams::MatchBySchedule(
      rule, GetTimePoint("2020-01-13T17:00:00+03:00") - 1s, kMoscowTimezone));
  EXPECT_TRUE(SelectDiscountParams::MatchBySchedule(
      rule, GetTimePoint("2020-01-13T17:00:00+03:00"), kMoscowTimezone));
  EXPECT_TRUE(SelectDiscountParams::MatchBySchedule(
      rule, GetTimePoint("2020-01-13T00:00:00+03:00") - 1s, kMoscowTimezone));
  EXPECT_FALSE(SelectDiscountParams::MatchBySchedule(
      rule, GetTimePoint("2020-01-13T00:00:00+03:00"), kMoscowTimezone));
}
