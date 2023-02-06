#include <gtest/gtest.h>

#include <memory>
#include <userver/utils/datetime.hpp>

#include <clients/billing-subventions-x/definitions.hpp>

#include <common_handlers/schedule/helpers.hpp>
#include <common_handlers/schedule_summary/rules.hpp>
#include <common_handlers/types.hpp>

#include "common.hpp"

namespace {
namespace bsx = clients::billing_subventions_x;
}  // namespace

struct BuildScheduleTestData {
  common_handlers::NewSchedule::value_type schedule;
  client_geoareas::models::SubventionGeoareas subvention_geoareas;

  cctz::civil_second from;
  cctz::civil_second to;
  cctz::time_zone timezone;

  std::vector<handlers::ScheduleDay> expected;
};

struct BuildScheduleTestParametrized
    : public ::testing::TestWithParam<BuildScheduleTestData> {};

TEST_P(BuildScheduleTestParametrized, Test) {
  handlers::SmartExtendedRule rule(
      subvention_matcher::GroupedRule{bsx::SingleRideRule{}},
      common_handlers::NewSchedule::value_type(GetParam().schedule),
      GetParam().subvention_geoareas, false);

  ASSERT_EQ(
      rule.GetSchedule(GetParam().from, GetParam().to, GetParam().timezone,
                       false, handlers::GetScheduleCheckPolicy::kDefault),
      GetParam().expected);
}

static const std::string kTimeFormat = "%Y-%m-%dT%H:%M:%SZ";

INSTANTIATE_TEST_SUITE_P(
    BuildScheduleTestParametrized, BuildScheduleTestParametrized,
    ::testing::ValuesIn({

        BuildScheduleTestData{
            common_handlers::NewSchedule::value_type{
                {
                    dt::Stringtime("2020-09-01T00:00:00Z"),  // Tue
                    dt::Stringtime("2020-09-02T00:00:00Z"),  // Tue
                },
                {},
            },
            {},
            cctz::convert(dt::Stringtime("2020-09-01T00:00:00Z"),
                          cctz::utc_time_zone()),  //
            cctz::convert(dt::Stringtime("2020-09-02T00:00:00Z"),
                          cctz::utc_time_zone()),  //
            cctz::utc_time_zone(),
            std::vector<handlers::ScheduleDay>{handlers::ScheduleDay{
                cctz::civil_day(
                    cctz::convert(dt::Stringtime("2020-09-01T00:00:00Z"),
                                  cctz::utc_time_zone())),
                cctz::civil_minute(
                    cctz::convert(dt::Stringtime("2020-09-01T00:00:00Z"),
                                  cctz::utc_time_zone())),
                cctz::civil_minute(
                    cctz::convert(dt::Stringtime("2020-09-02T00:00:00Z"),
                                  cctz::utc_time_zone())),
            }}  //
        },

        BuildScheduleTestData{
            common_handlers::NewSchedule::value_type{
                {
                    dt::Stringtime("2020-09-01T00:00:00Z"),  // Tue
                    dt::Stringtime("2020-09-03T00:00:00Z"),  // Tue
                },
                {},
            },
            {},
            cctz::convert(dt::Stringtime("2020-09-01T00:00:00Z"),
                          cctz::utc_time_zone()),  //
            cctz::convert(dt::Stringtime("2020-09-02T00:00:00Z"),
                          cctz::utc_time_zone()),  //
            cctz::utc_time_zone(),
            std::vector<handlers::ScheduleDay>{handlers::ScheduleDay{
                cctz::civil_day(
                    cctz::convert(dt::Stringtime("2020-09-01T00:00:00Z"),
                                  cctz::utc_time_zone())),
                cctz::civil_minute(
                    cctz::convert(dt::Stringtime("2020-09-01T00:00:00Z"),
                                  cctz::utc_time_zone())),
                cctz::civil_minute(
                    cctz::convert(dt::Stringtime("2020-09-02T00:00:00Z"),
                                  cctz::utc_time_zone())),
            }}  //
        },

        BuildScheduleTestData{
            common_handlers::NewSchedule::value_type{
                {
                    dt::Stringtime("2020-09-01T00:00:00Z"),  // Tue
                    dt::Stringtime("2020-09-02T00:00:00Z"),  // Tue
                },
                {},
            },
            {},
            cctz::convert(dt::Stringtime("2020-09-01T00:00:00Z"),
                          cctz::utc_time_zone()),  //
            cctz::convert(dt::Stringtime("2020-09-03T00:00:00Z"),
                          cctz::utc_time_zone()),  //
            cctz::utc_time_zone(),
            std::vector<handlers::ScheduleDay>{handlers::ScheduleDay{
                cctz::civil_day(
                    cctz::convert(dt::Stringtime("2020-09-01T00:00:00Z"),
                                  cctz::utc_time_zone())),
                cctz::civil_minute(
                    cctz::convert(dt::Stringtime("2020-09-01T00:00:00Z"),
                                  cctz::utc_time_zone())),
                cctz::civil_minute(
                    cctz::convert(dt::Stringtime("2020-09-02T00:00:00Z"),
                                  cctz::utc_time_zone())),
            }}  //
        },

        BuildScheduleTestData{
            common_handlers::NewSchedule::value_type{
                {
                    dt::Stringtime("2020-09-22T15:11:00Z"),  // Tue
                    dt::Stringtime("2020-09-24T16:40:00Z"),  // Tue
                },
                {},
            },
            {},
            cctz::convert(dt::Stringtime("2020-09-01T00:00:00Z"),
                          cctz::utc_time_zone()),  //
            cctz::convert(dt::Stringtime("2020-09-03T00:00:00Z"),
                          cctz::utc_time_zone()),  //
            cctz::utc_time_zone(),
            std::vector<handlers::ScheduleDay>{}  //
        },

    }));

struct MergeStepsData {
  std::vector<common_handlers::StepInfo> old_data;
  std::vector<common_handlers::StepInfo> new_data;
  std::vector<common_handlers::StepInfo> expected;
};

struct MergeStepsTestParametrized
    : public ::testing::TestWithParam<MergeStepsData> {};

TEST_P(MergeStepsTestParametrized, Test) {
  auto old = GetParam().old_data;
  handlers::MergeSteps(old, GetParam().new_data);

  ASSERT_EQ(old, GetParam().expected);
}

static common_handlers::StepInfo CreateStep(double amount) {
  common_handlers::StepInfo result;
  result.bonus_amount = amount;
  return result;
}

INSTANTIATE_TEST_SUITE_P(
    MergeStepsTestParametrized, MergeStepsTestParametrized,
    ::testing::ValuesIn({
        MergeStepsData{
            {CreateStep(10)},
            {CreateStep(20)},
            {CreateStep(10), CreateStep(20)},
        },
        MergeStepsData{
            {CreateStep(20)},
            {CreateStep(10)},
            {CreateStep(10), CreateStep(20)},
        },
        MergeStepsData{
            {CreateStep(10), CreateStep(20)},
            {CreateStep(30)},
            {CreateStep(10), CreateStep(20), CreateStep(30)},
        },
        MergeStepsData{
            {CreateStep(30)},
            {CreateStep(10), CreateStep(20)},
            {CreateStep(10), CreateStep(20), CreateStep(30)},
        },
        MergeStepsData{
            {CreateStep(30), CreateStep(40)},
            {CreateStep(10), CreateStep(20)},
            {CreateStep(10), CreateStep(20), CreateStep(30), CreateStep(40)},
        },
        MergeStepsData{
            {CreateStep(10), CreateStep(20)},
            {CreateStep(30), CreateStep(40)},
            {CreateStep(10), CreateStep(20), CreateStep(30), CreateStep(40)},
        },
        MergeStepsData{
            {CreateStep(10), CreateStep(40)},
            {CreateStep(20), CreateStep(30)},
            {CreateStep(10), CreateStep(40), CreateStep(20), CreateStep(30)},
        },
        MergeStepsData{
            {CreateStep(20), CreateStep(30)},
            {CreateStep(10), CreateStep(40)},
            {CreateStep(10), CreateStep(40), CreateStep(20), CreateStep(30)},
        },
        MergeStepsData{
            {},
            {CreateStep(10), CreateStep(40)},
            {CreateStep(10), CreateStep(40)},
        },
        MergeStepsData{
            {CreateStep(10), CreateStep(40)},
            {},
            {CreateStep(10), CreateStep(40)},
        },
    }));
