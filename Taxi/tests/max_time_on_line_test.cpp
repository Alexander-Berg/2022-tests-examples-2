#include <gtest/gtest.h>

#include <chrono>

#include <components/geobooking_drivers_unsubscriber.hpp>
#include <models/misc.hpp>
#include <userver/utils/mock_now.hpp>

namespace tests {
using namespace std::chrono_literals;
using DriversUnsubscriber = components::GeoBookingDriversUnsubscriber;
using utils::datetime::Stringtime;

namespace bs = clients::billing_subventions;

struct MaxTimeOnLineTestData {
  DriversUnsubscriber::GeoBookingRules rules;
  DriversUnsubscriber::SubscriptionsInfo subscriptions;
  std::chrono::minutes expected;
};

struct MaxTimeOnLineParametrized
    : public ::testing::TestWithParam<MaxTimeOnLineTestData> {};

models::TimePoint Now() {
  constexpr const char* kNow = "2020-01-10T23:15:55Z";
  return Stringtime(kNow, "UTC");
}

TEST_P(MaxTimeOnLineParametrized, Variants) {
  const auto param = GetParam();
  utils::datetime::MockNowSet(Now());
  const auto res =
      DriversUnsubscriber::GetMaxTimeOnLine(param.rules, param.subscriptions);
  ASSERT_EQ(res, param.expected);
}

bs::GeoBookingRule CreateRule(std::string_view start_hours,
                              std::string_view end_hours, std::string_view id) {
  bs::GeoBookingRule res;
  res.workshift.start = start_hours;
  res.workshift.end = end_hours;
  res.subvention_rule_id = id;
  res.time_zone.id = "UTC";
  return res;
}

static const auto RuleId1 = CreateRule("13:00", "20:00", "id1");

static const MaxTimeOnLineTestData kSubscriptionTodayBetweenRuleHours1 = {
    {RuleId1}, {"id1", Stringtime("2020-01-10T19:00:55Z", "UTC")}, 60min};

static const MaxTimeOnLineTestData kSubscriptionTodayBetweenRuleHours2 = {
    {RuleId1}, {"id1", Stringtime("2020-01-10T15:45:55Z", "UTC")}, 255min};

static const MaxTimeOnLineTestData kSubscriptionBeforeRuleStart = {
    {RuleId1}, {"id1", Stringtime("2020-01-10T10:00:55Z", "UTC")}, 420min};

static const MaxTimeOnLineTestData kSubscriptionAfterRuleEnd = {
    {RuleId1}, {"id1", Stringtime("2020-01-10T20:01:55Z", "UTC")}, 0min};

static const MaxTimeOnLineTestData kSubscriptionYesterday = {
    {RuleId1}, {"id1", Stringtime("2020-01-09T17:00:55Z", "UTC")}, 420min};

// --------------------------------------------------------------------------------------------------------------//

static const auto RuleId2 = CreateRule("20:00", "23:00", "id2");

static const MaxTimeOnLineTestData kSubscriptionTodayBetweenRuleHours1TwoRules =
    {{RuleId1, RuleId2},
     {"id1", Stringtime("2020-01-10T19:00:55Z", "UTC")},
     60min + 180min};

static const MaxTimeOnLineTestData kSubscriptionTodayBetweenRuleHours2TwoRules =
    {{RuleId1, RuleId2},
     {"id1", Stringtime("2020-01-10T15:45:55Z", "UTC")},
     255min + 180min};

static const MaxTimeOnLineTestData kSubscriptionTodayBetweenRuleHours3TwoRules =
    {{RuleId1, RuleId2},
     {"id1", Stringtime("2020-01-10T20:45:55Z", "UTC")},
     135min};

static const MaxTimeOnLineTestData kSubscriptionBeforeRuleStartTwoRules = {
    {RuleId1, RuleId2},
    {"id1", Stringtime("2020-01-10T10:00:55Z", "UTC")},
    420min + 180min};

static const MaxTimeOnLineTestData kSubscriptionAfterRuleEndTwoRules = {
    {RuleId1, RuleId2},
    {"id1", Stringtime("2020-01-10T20:01:55Z", "UTC")},
    0min + 179min};

static const MaxTimeOnLineTestData kSubscriptionYesterdayTwoRules = {
    {RuleId1, RuleId2},
    {"id1", Stringtime("2020-01-09T17:00:55Z", "UTC")},
    420min + 180min};

const std::vector<MaxTimeOnLineTestData> kMaxTimeOnLineTestDataVariants = {
    kSubscriptionTodayBetweenRuleHours1,
    kSubscriptionTodayBetweenRuleHours2,
    kSubscriptionBeforeRuleStart,
    kSubscriptionAfterRuleEnd,
    kSubscriptionYesterday,
    kSubscriptionTodayBetweenRuleHours1TwoRules,
    kSubscriptionTodayBetweenRuleHours2TwoRules,
    kSubscriptionTodayBetweenRuleHours3TwoRules,
    kSubscriptionBeforeRuleStartTwoRules,
    kSubscriptionAfterRuleEndTwoRules,
    kSubscriptionYesterdayTwoRules};

INSTANTIATE_TEST_SUITE_P(MaxTimeOnLine, MaxTimeOnLineParametrized,
                         ::testing::ValuesIn(kMaxTimeOnLineTestDataVariants));
}  // namespace tests
