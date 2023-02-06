#include <gtest/gtest.h>

#include <cctz/time_zone.h>

#include <set>

#include <userver/utils/datetime.hpp>

#include <subvention_matcher/impl/impl.hpp>
#include <subvention_matcher/impl/transform/transform.hpp>
#include <subvention_matcher/schedule/schedule.hpp>
#include <subvention_matcher/types.hpp>

#include "common.hpp"

using namespace subvention_matcher;
using namespace subvention_matcher::schedule;

struct ScheduleTestData {
  TimeRange time_range;
  std::vector<Rate> rates;
  cctz::time_zone timezone;

  RuleSchedule expected;
};

struct ScheduleTestParametrized
    : public ::testing::TestWithParam<ScheduleTestData> {};

TEST_P(ScheduleTestParametrized, Test) {
  ASSERT_EQ(GetSchedule(GetParam().time_range, "test_rule", GetParam().rates,
                        GetParam().timezone),
            GetParam().expected);
}

static const std::string kTimeFormat = "%Y-%m-%dT%H:%M:%SZ";

using wd = clients::billing_subventions_x::WeekDay;

INSTANTIATE_TEST_SUITE_P(
    ScheduleTestParametrized, ScheduleTestParametrized,
    ::testing::ValuesIn({
        ScheduleTestData{
            TimeRange{
                dt::Stringtime("2021-01-28T15:00:00Z", "Europe/Moscow",
                               kTimeFormat),
                dt::Stringtime("2021-02-04T15:00:00Z", "Europe/Moscow",
                               kTimeFormat),
            },
            std::vector<Rate>{
                Rate{wd::kMon, "00:00", "100.0"},  //
                Rate{wd::kTue, "00:00", "100.0"},  //
                Rate{wd::kWed, "00:00", "100.0"},  //
                Rate{wd::kFri, "00:00", "100.0"},  ///
                Rate{wd::kSat, "00:00", "100.0"},  //
                Rate{wd::kSun, "00:00", "100.0"},  //
                Rate{wd::kMon, "00:00", "0.0"},    //
            },
            GetMskTz(),  //
            RuleSchedule{
                {TimeRange{
                     dt::Stringtime("2021-01-28T12:00:00Z"),
                     dt::Stringtime("2021-01-31T21:00:00Z"),
                 },
                 100.0},
                {TimeRange{
                     dt::Stringtime("2021-02-01T21:00:00Z"),
                     dt::Stringtime("2021-02-04T12:00:00Z"),
                 },
                 100.0},
            }  //
        },

        ScheduleTestData{
            TimeRange{
                dt::Stringtime("2020-09-01T00:00:00Z"),  // Tue
                dt::Stringtime("2020-09-08T00:00:00Z"),  // Tue
            },
            std::vector<Rate>{},    //
            cctz::utc_time_zone(),  //
            RuleSchedule{}          //
        },

        ScheduleTestData{
            TimeRange{
                dt::Stringtime("2020-09-01T00:00:00Z"),  // Tue
                dt::Stringtime("2020-09-08T00:00:00Z"),  // Tue
            },
            std::vector<Rate>{
                Rate{wd::kMon, "00:00", "100.0"},  //
            },
            cctz::utc_time_zone(),  //
            RuleSchedule{
                {TimeRange{
                     dt::Stringtime("2020-09-01T00:00:00Z"),  // Tue
                     dt::Stringtime("2020-09-08T00:00:00Z"),  // Tue
                 },
                 100.0},
            }  //
        },

        ScheduleTestData{
            TimeRange{
                dt::Stringtime("2020-09-01T00:00:00Z", "Europe/Moscow",
                               kTimeFormat),  // Tue
                dt::Stringtime("2020-09-08T00:00:00Z", "Europe/Moscow",
                               kTimeFormat),  // Tue
            },
            std::vector<Rate>{
                Rate{wd::kMon, "00:00", "100.0"},  //
            },
            GetMskTz(),  //
            RuleSchedule{
                {TimeRange{
                     dt::Stringtime("2020-08-31T21:00:00Z"),  // Tue
                     dt::Stringtime("2020-09-07T21:00:00Z"),  // Tue
                 },
                 100.0},
            }  //
        },

        ScheduleTestData{
            TimeRange{
                dt::Stringtime("2020-09-01T00:00:00Z"),  // Tue
                dt::Stringtime("2020-09-08T00:00:00Z"),  // Tue
            },
            std::vector<Rate>{
                Rate{wd::kWed, "00:00", "100.0"},  //
            },
            cctz::utc_time_zone(),  //
            RuleSchedule{
                {TimeRange{
                     dt::Stringtime("2020-09-01T00:00:00Z"),  // Tue
                     dt::Stringtime("2020-09-08T00:00:00Z"),  // Tue
                 },
                 100.0},
            }  //
        },

        ScheduleTestData{
            TimeRange{
                dt::Stringtime("2020-09-01T00:00:00Z"),  // Tue
                dt::Stringtime("2020-09-08T00:00:00Z"),  // Tue
            },
            std::vector<Rate>{
                Rate{wd::kWed, "00:00", "100.0"},  //
                Rate{wd::kFri, "00:00", "200.0"},  //
            },
            cctz::utc_time_zone(),  //
            RuleSchedule{
                {TimeRange{
                     dt::Stringtime("2020-09-01T00:00:00Z"),  // Tue
                     dt::Stringtime("2020-09-02T00:00:00Z"),  // Wed
                 },
                 200.0},
                {TimeRange{
                     dt::Stringtime("2020-09-02T00:00:00Z"),  // Wed
                     dt::Stringtime("2020-09-04T00:00:00Z"),  // Fri
                 },
                 100.0},
                {TimeRange{
                     dt::Stringtime("2020-09-04T00:00:00Z"),  // Fri
                     dt::Stringtime("2020-09-08T00:00:00Z"),  // Tue
                 },
                 200.0},
            }  //
        },

        ScheduleTestData{
            TimeRange{
                dt::Stringtime("2020-09-01T00:00:00Z"),  // Tue
                dt::Stringtime("2020-09-08T00:00:00Z"),  // Tue
            },

            std::vector<Rate>{
                Rate{wd::kMon, "00:00", "0.0"},    //
                Rate{wd::kTue, "00:00", "100.0"},  //
            },

            cctz::utc_time_zone(),  //

            RuleSchedule{
                {TimeRange{
                     dt::Stringtime("2020-09-01T00:00:00Z"),  // Tue
                     dt::Stringtime("2020-09-07T00:00:00Z"),  // Mon
                 },
                 100.0},
            }},

        ScheduleTestData{
            TimeRange{
                dt::Stringtime("2020-09-01T00:00:00Z"),  // Tue
                dt::Stringtime("2020-09-08T00:00:00Z"),  // Tue
            },

            std::vector<Rate>{
                Rate{wd::kMon, "00:00", "0.0"},    //
                Rate{wd::kTue, "00:00", "100.0"},  //
                Rate{wd::kTue, "12:00", "0.0"},    //
            },

            cctz::utc_time_zone(),  //

            RuleSchedule{
                {TimeRange{
                     dt::Stringtime("2020-09-01T00:00:00Z"),  // Tue
                     dt::Stringtime("2020-09-01T12:00:00Z"),  // Tue
                 },
                 100.0},
            }},

        ScheduleTestData{
            TimeRange{
                dt::Stringtime("2020-09-01T00:00:00Z"),  // Tue
                dt::Stringtime("2020-09-08T00:00:00Z"),  // Tue
            },

            std::vector<Rate>{
                Rate{wd::kMon, "00:00", "0.0"},    //
                Rate{wd::kTue, "00:00", "100.0"},  //
                Rate{wd::kTue, "12:00", "0.0"},    //
                Rate{wd::kFri, "12:00", "30.0"},   //
            },

            cctz::utc_time_zone(),  //

            RuleSchedule{
                {TimeRange{
                     dt::Stringtime("2020-09-01T00:00:00Z"),  // Tue
                     dt::Stringtime("2020-09-01T12:00:00Z"),  // Tue
                 },
                 100.0},
                {TimeRange{
                     dt::Stringtime("2020-09-04T12:00:00Z"),  // Fri
                     dt::Stringtime("2020-09-07T00:00:00Z"),  // Mon
                 },
                 30.0},
            }},

        ScheduleTestData{
            TimeRange{
                dt::Stringtime("2020-09-01T00:00:00Z"),  // Tue
                dt::Stringtime("2020-09-08T00:00:00Z"),  // Tue
            },

            std::vector<Rate>{
                Rate{wd::kMon, "21:00", "300.0"},  //
                Rate{wd::kTue, "09:00", "0.0"},    //
                Rate{wd::kWed, "18:00", "500.0"},  //
                Rate{wd::kThu, "05:00", "0.0"},    //
            },

            cctz::utc_time_zone(),  //

            RuleSchedule{
                {TimeRange{
                     dt::Stringtime("2020-09-01T00:00:00Z"),  // Tue
                     dt::Stringtime("2020-09-01T09:00:00Z"),  // Tue
                 },
                 300.0},
                {TimeRange{
                     dt::Stringtime("2020-09-02T18:00:00Z"),  // Fri
                     dt::Stringtime("2020-09-03T05:00:00Z"),  // Mon
                 },
                 500.0},
                {TimeRange{
                     dt::Stringtime("2020-09-07T21:00:00Z"),  // Fri
                     dt::Stringtime("2020-09-08T00:00:00Z"),  // Mon
                 },
                 300.0},
            }},

        ScheduleTestData{
            TimeRange{
                dt::Stringtime("2020-09-01T00:00:00Z"),  // Tue
                dt::Stringtime("2020-09-08T00:00:00Z"),  // Tue
            },

            std::vector<Rate>{
                Rate{wd::kMon, "21:00", "0.0"},    //
                Rate{wd::kTue, "09:00", "200.0"},  //
                Rate{wd::kWed, "18:00", "0.0"},    //
                Rate{wd::kThu, "05:00", "400.0"},  //
            },

            cctz::utc_time_zone(),  //

            RuleSchedule{
                {TimeRange{
                     dt::Stringtime("2020-09-01T09:00:00Z"),  // Tue
                     dt::Stringtime("2020-09-02T18:00:00Z"),  // Wed
                 },
                 200.0},
                {TimeRange{
                     dt::Stringtime("2020-09-03T05:00:00Z"),  // Thu
                     dt::Stringtime("2020-09-07T21:00:00Z"),  // Mon
                 },
                 400.0},
            }},
    }));

struct MergeContinuousIntervalsTestData {
  Schedule rule_schedule;
  Schedule expected_merged_schedule;
  bool throws_overlap_exception = false;
  bool merge_included_intervals = false;
  bool merge_overlapped_intervals = false;
};

struct MergeContinuousIntervalsTestDataParametrized
    : public BaseTestWithParam<MergeContinuousIntervalsTestData> {};

TEST_P(MergeContinuousIntervalsTestDataParametrized, Test) {
  auto schedule = GetParam().rule_schedule;
  if (GetParam().throws_overlap_exception) {
    ASSERT_THROW(impl::transform::MergeContinuousIntervals(schedule),
                 impl::IntervalsOverlap);
  } else {
    impl::transform::MergeContinuousIntervals(schedule);

    ASSERT_EQ(schedule, GetParam().expected_merged_schedule);
  }
}

static const TimePoint kStart = dt::Stringtime("2020-09-01T00:00:00Z");
using hours = std::chrono::hours;

static const subvention_matcher::ScheduleItem kScheduleItemA{{}, 100.};
static const subvention_matcher::ScheduleItem kScheduleItemB{{}, 200.};

INSTANTIATE_TEST_SUITE_P(
    MergeContinuousIntervalsTestDataParametrized,
    MergeContinuousIntervalsTestDataParametrized,
    ::testing::ValuesIn({
        MergeContinuousIntervalsTestData{},

        MergeContinuousIntervalsTestData{
            {
                {{kStart, kStart + hours(2)}, kScheduleItemA},
                {{kStart + hours(2), kStart + hours(3)}, kScheduleItemA},
            },
            {
                {{kStart, kStart + hours(3)}, kScheduleItemA},
            },
        },

        MergeContinuousIntervalsTestData{
            {
                {{kStart, kStart + hours(2)}, kScheduleItemA},
                {{kStart + hours(1), kStart + hours(3)}, kScheduleItemB},
            },
            {},
            true,
        },

        MergeContinuousIntervalsTestData{
            {
                {{kStart, kStart + hours(2)}, kScheduleItemA},
                {{kStart + hours(2), kStart + hours(3)}, kScheduleItemB},
            },
            {
                {{kStart, kStart + hours(2)}, kScheduleItemA},
                {{kStart + hours(2), kStart + hours(3)}, kScheduleItemB},
            },
        },

        MergeContinuousIntervalsTestData{
            {
                {{kStart, kStart + hours(2)}, kScheduleItemA},
                {{kStart + hours(2), kStart + hours(3)}, kScheduleItemA},
            },
            {
                {{kStart, kStart + hours(3)}, kScheduleItemA},
            },
        },

        MergeContinuousIntervalsTestData{
            {
                {{kStart, kStart + hours(2)}, kScheduleItemA},
                {{kStart + hours(2), kStart + hours(3)}, kScheduleItemA},
                {{kStart + hours(4), kStart + hours(5)}, kScheduleItemA},
                {{kStart + hours(5), kStart + hours(7)}, kScheduleItemA},
                {{kStart + hours(8), kStart + hours(9)}, kScheduleItemA},
            },
            {
                {{kStart, kStart + hours(3)}, kScheduleItemA},
                {{kStart + hours(4), kStart + hours(7)}, kScheduleItemA},
                {{kStart + hours(8), kStart + hours(9)}, kScheduleItemA},
            },
        },

        MergeContinuousIntervalsTestData{
            {
                {{kStart, kStart + hours(2)}, kScheduleItemA},
                {{kStart + hours(2), kStart + hours(3)}, kScheduleItemA},
                {{kStart + hours(3), kStart + hours(5)}, kScheduleItemA},
                {{kStart + hours(5), kStart + hours(7)}, kScheduleItemA},
                {{kStart + hours(7), kStart + hours(9)}, kScheduleItemA},
            },
            {
                {{kStart, kStart + hours(9)}, kScheduleItemA},
            },
        },

        MergeContinuousIntervalsTestData{
            {
                {{kStart, kStart + hours(2)}, kScheduleItemA},
                {{kStart + hours(1), kStart + hours(3)}, kScheduleItemA},
                {{kStart + hours(3), kStart + hours(5)}, kScheduleItemA},
                {{kStart + hours(5), kStart + hours(7)}, kScheduleItemA},
                {{kStart + hours(7), kStart + hours(9)}, kScheduleItemA},
                {{kStart + hours(2), kStart + hours(9)}, kScheduleItemA},
            },
            {},
            true,
        },

        MergeContinuousIntervalsTestData{
            {
                {{kStart, kStart + hours(2)}, kScheduleItemA},
                {{kStart + hours(1), kStart + hours(3)}, kScheduleItemA},
                {{kStart + hours(3), kStart + hours(5)}, kScheduleItemA},
                {{kStart + hours(5), kStart + hours(7)}, kScheduleItemA},
                {{kStart + hours(7), kStart + hours(9)}, kScheduleItemA},
                {{kStart, kStart + hours(9)}, kScheduleItemA},
            },
            {},
            true,
        },

        MergeContinuousIntervalsTestData{
            {
                {{kStart, kStart + hours(2)}, kScheduleItemA},
                {{kStart + hours(2), kStart + hours(3)}, kScheduleItemA},
                {{kStart + hours(2), kStart + hours(5)}, kScheduleItemB},
                {{kStart + hours(5), kStart + hours(7)}, kScheduleItemA},
                {{kStart + hours(7), kStart + hours(9)}, kScheduleItemA},
            },
            {},
            true,
        },

        MergeContinuousIntervalsTestData{
            {
                {{kStart, kStart + hours(1)}, kScheduleItemA},
                {{kStart + hours(1), kStart + hours(2)}, kScheduleItemA},
                {{kStart + hours(2), kStart + hours(5)}, kScheduleItemB},
                {{kStart + hours(5), kStart + hours(7)}, kScheduleItemA},
                {{kStart + hours(7), kStart + hours(9)}, kScheduleItemA},
            },
            {
                {{kStart, kStart + hours(2)}, kScheduleItemA},
                {{kStart + hours(2), kStart + hours(5)}, kScheduleItemB},
                {{kStart + hours(5), kStart + hours(9)}, kScheduleItemA},
            },
        },

        // 11
        MergeContinuousIntervalsTestData{
            {
                {{kStart, kStart + hours(4)}, kScheduleItemA},
                {{kStart + hours(2), kStart + hours(3)}, kScheduleItemA},
            },
            {},
            true,
        },

        MergeContinuousIntervalsTestData{
            {
                {{kStart, kStart + hours(2)}, kScheduleItemA},
                {{kStart + hours(1), kStart + hours(3)}, kScheduleItemA},
            },
            {},
            true,
        },
    }));

namespace {

Rule CreateRule(const std::string& id) {
  Rule result;
  result.id = id;
  return result;
}

}  // namespace

static const Rule kRuleA = CreateRule("cfed96ef-8f26-45d2-b90f-33ea16af2a82");
static const Rule kRuleB = CreateRule("265f213d-ea43-49f2-8b60-5231d10e9ce1");
static const Rule kRuleC = CreateRule("e2d38b4a-86f0-44e7-8354-1172cbb1a462");
static const Rule kRuleD = CreateRule("8e56489d-1d4f-4b68-8389-e45e2b220bbb");
static const Rule kRuleE = CreateRule("4ac50620-dc4f-41d1-877a-bdfb912f3089");
static const Rule kRuleF = CreateRule("07e6c470-5d8c-4286-bda9-0cdd7f571ad3");
static const Rule kRuleG = CreateRule("754f64a2-384c-43d1-a56b-4faab3a06af6");

struct ToScheduleTestData {
  KeyPointRuleMatches keypoints;
  RuleMatchesSchedule expected;
  RuleMatchesSchedule expected_merged;
};

struct ToScheduleTestParametrized
    : public ::testing::TestWithParam<ToScheduleTestData> {};

TEST_P(ToScheduleTestParametrized, Test) {
  auto result = subvention_matcher::impl::transform::ToSchedule(
      KeyPointRuleMatches(GetParam().keypoints));
  ASSERT_EQ(result, GetParam().expected);
  for (auto& [_, schedule] : result) {
    impl::transform::MergeContinuousIntervals(schedule);
  }
  ASSERT_EQ(result, GetParam().expected_merged);
}

using PT = PropertyType;
using PS = PropertySource;
static const DriverPropertyMap kDefaultPropertyMap{
    {PT::kBranding, {BrandingProperty{{false, false}}, PS::kDriver}},  //
    {PT::kActivity, {ActivityProperty{{50}}, PS::kDriver}},            //
    {PT::kTags, {TagsProperty{{{"tag"}}}, PS::kDriver}},               //
    {PT::kZone, {ZoneProperty{{"zone"}}, PS::kDriver}},                //
    {PT::kClass, {ClassProperty{{"class"}}, PS::kDriver}},             //
};

INSTANTIATE_TEST_SUITE_P(
    ToScheduleTestParametrized, ToScheduleTestParametrized,
    ::testing::ValuesIn({
        ToScheduleTestData{
            KeyPointRuleMatches{
                {
                    dt::Stringtime("2020-09-21T21:00:00Z"),
                    RuleScheduleMatches{
                        {kRuleA, {kDefaultPropertyMap, 502}},
                    },
                },
                {
                    dt::Stringtime("2020-09-22T07:05:00Z"),
                    RuleScheduleMatches{
                        {kRuleA, {kDefaultPropertyMap, 502}},
                    },
                },
                {
                    dt::Stringtime("2020-09-22T10:15:00Z"),
                    RuleScheduleMatches{},
                },
                {
                    dt::Stringtime("2020-09-22T10:30:00Z"),
                    RuleScheduleMatches{},
                },
                {
                    dt::Stringtime("2020-09-22T12:40:00Z"),
                    RuleScheduleMatches{
                        {kRuleA, {kDefaultPropertyMap, 503}},
                    },
                },
                {
                    dt::Stringtime("2020-09-22T13:00:00Z"),
                    RuleScheduleMatches{
                        {kRuleA, {kDefaultPropertyMap, 503}},
                    },
                },
                {
                    dt::Stringtime("2020-09-22T15:11:00Z"),
                    RuleScheduleMatches{
                        {kRuleA, {kDefaultPropertyMap, 504}},
                    },
                },
                {
                    dt::Stringtime("2020-09-22T20:15:00Z"),
                    RuleScheduleMatches{
                        {kRuleA, {kDefaultPropertyMap, 504}},
                    },
                },
                {
                    dt::Stringtime("2020-09-22T20:20:00Z"),
                    RuleScheduleMatches{
                        {kRuleA, {kDefaultPropertyMap, 504}},
                    },
                },
                {
                    dt::Stringtime("2020-09-24T16:40:00Z"),
                    RuleScheduleMatches{
                        {kRuleA, {kDefaultPropertyMap, 505}},
                    },
                },
                {
                    dt::Stringtime("2020-09-24T20:10:00Z"),
                    RuleScheduleMatches{
                        {kRuleA, {{}, 0}},
                    },
                },
            },
            RuleMatchesSchedule{
                {
                    kRuleA,
                    Schedule{
                        {
                            {
                                dt::Stringtime("2020-09-21T21:00:00Z"),
                                dt::Stringtime("2020-09-22T07:05:00Z"),
                            },
                            {kDefaultPropertyMap, 502},
                        },
                        {
                            {
                                dt::Stringtime("2020-09-22T07:05:00Z"),
                                dt::Stringtime("2020-09-22T10:15:00Z"),
                            },
                            {kDefaultPropertyMap, 502},
                        },
                        {
                            {
                                dt::Stringtime("2020-09-22T12:40:00Z"),
                                dt::Stringtime("2020-09-22T13:00:00Z"),
                            },
                            {kDefaultPropertyMap, 503},
                        },
                        {
                            {
                                dt::Stringtime("2020-09-22T13:00:00Z"),
                                dt::Stringtime("2020-09-22T15:11:00Z"),
                            },
                            {kDefaultPropertyMap, 503},
                        },
                        {
                            {
                                dt::Stringtime("2020-09-22T15:11:00Z"),
                                dt::Stringtime("2020-09-22T20:15:00Z"),
                            },
                            {kDefaultPropertyMap, 504},
                        },
                        {
                            {
                                dt::Stringtime("2020-09-22T20:15:00Z"),
                                dt::Stringtime("2020-09-22T20:20:00Z"),
                            },
                            {kDefaultPropertyMap, 504},
                        },
                        {
                            {
                                dt::Stringtime("2020-09-22T20:20:00Z"),
                                dt::Stringtime("2020-09-24T16:40:00Z"),
                            },
                            {kDefaultPropertyMap, 504},
                        },
                        {
                            {
                                dt::Stringtime("2020-09-24T16:40:00Z"),
                                dt::Stringtime("2020-09-24T20:10:00Z"),
                            },
                            {kDefaultPropertyMap, 505},
                        },
                    },
                },
            },
            RuleMatchesSchedule{
                {
                    kRuleA,
                    Schedule{
                        {
                            {
                                dt::Stringtime("2020-09-21T21:00:00Z"),
                                dt::Stringtime("2020-09-22T10:15:00Z"),
                            },
                            {kDefaultPropertyMap, 502},
                        },
                        {
                            {
                                dt::Stringtime("2020-09-22T12:40:00Z"),
                                dt::Stringtime("2020-09-22T15:11:00Z"),
                            },
                            {kDefaultPropertyMap, 503},
                        },
                        {
                            {
                                dt::Stringtime("2020-09-22T15:11:00Z"),
                                dt::Stringtime("2020-09-24T16:40:00Z"),
                            },
                            {kDefaultPropertyMap, 504},
                        },
                        {
                            {
                                dt::Stringtime("2020-09-24T16:40:00Z"),
                                dt::Stringtime("2020-09-24T20:10:00Z"),
                            },
                            {kDefaultPropertyMap, 505},
                        },
                    },
                },
            },
        },
    }));

struct GroupRulesTestData {
  Rules rules;
  PropertyTypes types;
  std::map<std::set<Property>, Rules> expected;
};

struct GroupRulesTestParametrized
    : public ::testing::TestWithParam<GroupRulesTestData> {};

TEST_P(GroupRulesTestParametrized, Test) {
  auto result = subvention_matcher::impl::transform::GroupRules(
      Rules{GetParam().rules}, GetParam().types);
  ASSERT_EQ(result, GetParam().expected);
}

static const Rule lRMskNoneEco10 =
    CreateRule("moscow", std::nullopt, "econom", 10);
static const Rule lRMskNoneEco20 =
    CreateRule("moscow", std::nullopt, "econom", 20);

static const Rule lRMskZone1Eco10 = CreateRule("moscow", "Zone1", "econom", 10);

static const Rule lRMskZone2Eco10 = CreateRule("moscow", "Zone2", "econom", 10);

static const Rule lRMskNoneComf10 =
    CreateRule("moscow", std::nullopt, "comfort", 10);
static const Rule lREkbNoneComf10 =
    CreateRule("ekb", std::nullopt, "comfort", 10);

static const Rule lREkbZone1Comf10 = CreateRule("ekb", "Zone1", "comfort", 10);

static const Rule lREkbZone2Comf10 = CreateRule("ekb", "Zone2", "comfort", 10);

INSTANTIATE_TEST_SUITE_P(
    GroupRulesTestParametrized, GroupRulesTestParametrized,
    ::testing::ValuesIn({

        GroupRulesTestData{
            {lRMskNoneEco10, lRMskZone1Eco10, lRMskZone2Eco10, lREkbNoneComf10,
             lREkbZone1Comf10, lREkbZone2Comf10},
            {PT::kZone},
            {
                {{ZoneProperty{{"moscow"}}},
                 {lRMskNoneEco10, lRMskZone1Eco10, lRMskZone2Eco10}},
                {{ZoneProperty{{"ekb"}}},
                 {lREkbNoneComf10, lREkbZone1Comf10, lREkbZone2Comf10}},
            },
        },

        GroupRulesTestData{
            {lRMskNoneEco10, lRMskZone1Eco10, lRMskZone2Eco10, lREkbNoneComf10,
             lREkbZone1Comf10, lREkbZone2Comf10},
            {PT::kGeoarea},
            {
                {{GeoareaProperty{{}}}, {lRMskNoneEco10, lREkbNoneComf10}},
                {{GeoareaProperty{{"Zone1"}}},
                 {lRMskZone1Eco10, lREkbZone1Comf10}},
                {{GeoareaProperty{{"Zone2"}}},
                 {lRMskZone2Eco10, lREkbZone2Comf10}},
            },
        },

        GroupRulesTestData{
            {lRMskNoneEco10, lRMskZone1Eco10, lRMskZone2Eco10, lREkbNoneComf10,
             lREkbZone1Comf10, lREkbZone2Comf10},
            {PT::kClass},
            {
                {{ClassProperty{{"econom"}}},
                 {lRMskNoneEco10, lRMskZone1Eco10, lRMskZone2Eco10}},
                {{ClassProperty{{"comfort"}}},
                 {lREkbNoneComf10, lREkbZone1Comf10, lREkbZone2Comf10}},
            },
        },

        GroupRulesTestData{
            {lRMskNoneEco10, lRMskZone1Eco10, lRMskZone2Eco10, lREkbNoneComf10,
             lREkbZone1Comf10, lREkbZone2Comf10},
            {PT::kZone, PT::kGeoarea},
            {
                {{ZoneProperty{{"moscow"}}, GeoareaProperty{{}}},
                 {lRMskNoneEco10}},
                {{ZoneProperty{{"ekb"}}, GeoareaProperty{{}}},
                 {lREkbNoneComf10}},

                {{ZoneProperty{{"moscow"}}, GeoareaProperty{{"Zone1"}}},
                 {lRMskZone1Eco10}},
                {{ZoneProperty{{"ekb"}}, GeoareaProperty{{"Zone1"}}},
                 {lREkbZone1Comf10}},

                {{ZoneProperty{{"moscow"}}, GeoareaProperty{{"Zone2"}}},
                 {lRMskZone2Eco10}},
                {{ZoneProperty{{"ekb"}}, GeoareaProperty{{"Zone2"}}},
                 {lREkbZone2Comf10}},
            },
        },

        GroupRulesTestData{
            {lRMskNoneEco10, lRMskZone1Eco10, lRMskZone2Eco10, lREkbNoneComf10,
             lREkbZone1Comf10, lREkbZone2Comf10},
            {PT::kZone, PT::kClass},
            {
                {{ZoneProperty{{"moscow"}}, ClassProperty{{"econom"}}},
                 {lRMskNoneEco10, lRMskZone1Eco10, lRMskZone2Eco10}},
                {{ZoneProperty{{"ekb"}}, ClassProperty{{"comfort"}}},
                 {lREkbNoneComf10, lREkbZone1Comf10, lREkbZone2Comf10}},
            },
        },

        GroupRulesTestData{
            {lRMskNoneEco10, lRMskZone1Eco10, lRMskZone2Eco10, lREkbNoneComf10,
             lREkbZone1Comf10, lREkbZone2Comf10},
            {PT::kZone, PT::kGeoarea, PT::kClass},
            {
                {{ZoneProperty{{"moscow"}}, GeoareaProperty{{}},
                  ClassProperty{{"econom"}}},
                 {lRMskNoneEco10}},
                {{ZoneProperty{{"ekb"}}, GeoareaProperty{{}},
                  ClassProperty{{"comfort"}}},
                 {lREkbNoneComf10}},

                {{ZoneProperty{{"moscow"}}, GeoareaProperty{{"Zone1"}},
                  ClassProperty{{"econom"}}},
                 {lRMskZone1Eco10}},
                {{ZoneProperty{{"ekb"}}, GeoareaProperty{{"Zone1"}},
                  ClassProperty{{"comfort"}}},
                 {lREkbZone1Comf10}},

                {{ZoneProperty{{"moscow"}}, GeoareaProperty{{"Zone2"}},
                  ClassProperty{{"econom"}}},
                 {lRMskZone2Eco10}},
                {{ZoneProperty{{"ekb"}}, GeoareaProperty{{"Zone2"}},
                  ClassProperty{{"comfort"}}},
                 {lREkbZone2Comf10}},
            },
        },

        GroupRulesTestData{
            {lRMskNoneEco10, lRMskNoneEco20, lRMskNoneComf10, lRMskZone1Eco10,
             lRMskZone2Eco10, lREkbNoneComf10, lREkbZone1Comf10,
             lREkbZone2Comf10},
            {PT::kZone, PT::kGeoarea, PT::kClass},
            {
                {{ZoneProperty{{"moscow"}}, GeoareaProperty{{}},
                  ClassProperty{{"econom"}}},
                 {lRMskNoneEco10, lRMskNoneEco20}},
                {{ZoneProperty{{"moscow"}}, GeoareaProperty{{}},
                  ClassProperty{{"comfort"}}},
                 {lRMskNoneComf10}},
                {{ZoneProperty{{"ekb"}}, GeoareaProperty{{}},
                  ClassProperty{{"comfort"}}},
                 {lREkbNoneComf10}},

                {{ZoneProperty{{"moscow"}}, GeoareaProperty{{"Zone1"}},
                  ClassProperty{{"econom"}}},
                 {lRMskZone1Eco10}},
                {{ZoneProperty{{"ekb"}}, GeoareaProperty{{"Zone1"}},
                  ClassProperty{{"comfort"}}},
                 {lREkbZone1Comf10}},

                {{ZoneProperty{{"moscow"}}, GeoareaProperty{{"Zone2"}},
                  ClassProperty{{"econom"}}},
                 {lRMskZone2Eco10}},
                {{ZoneProperty{{"ekb"}}, GeoareaProperty{{"Zone2"}},
                  ClassProperty{{"comfort"}}},
                 {lREkbZone2Comf10}},
            },
        },
    }));
