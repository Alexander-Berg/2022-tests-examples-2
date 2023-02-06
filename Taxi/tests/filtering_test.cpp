#include <gtest/gtest.h>

#include <subvention_matcher/impl/properties/filtering.hpp>

#include "common.hpp"

using namespace subvention_matcher;
using namespace subvention_matcher::impl::properties;

struct FloorActivityData {
  DriverProperties driver_activity;
  DriverProperties rules_activities;
  ActivityInterval expected;
  DriverProperties expected_driver_activity;
};

struct FloorActivityParametrized : public BaseTestWithParam<FloorActivityData> {
};

TEST_P(FloorActivityParametrized, Test) {
  auto driver_activity = GetParam().driver_activity;
  auto rules_activities = GetParam().rules_activities;

  const auto interval = GetActivityInterval(driver_activity, rules_activities);
  ASSERT_EQ(interval, GetParam().expected);

  FloorActivity(interval, driver_activity, std::move(rules_activities));
  ASSERT_EQ(GetParam().expected_driver_activity, driver_activity);
}

INSTANTIATE_TEST_SUITE_P(
    FloorActivityParametrized, FloorActivityParametrized,
    ::testing::ValuesIn({
        FloorActivityData{
            {
                {ActivityProperty{{41}}, PropertySource::kDriver},
            },
            {
                {ActivityProperty{{41}}, PropertySource::kFake},
            },
            {41, 100},
            {
                {ActivityProperty{{41}}, PropertySource::kDriver},
            },
        },

        FloorActivityData{
            {
                {ActivityProperty{{50}}, PropertySource::kDriver},
            },
            {
                {ActivityProperty{{41}}, PropertySource::kFake},
            },
            {41, 100},
            {
                {ActivityProperty{{41}}, PropertySource::kDriver},
            },
        },

        FloorActivityData{
            {
                {ActivityProperty{{10}}, PropertySource::kDriver},
            },
            {
                {ActivityProperty{{41}}, PropertySource::kFake},
            },
            {0, 40},
            {
                {ActivityProperty{{0}}, PropertySource::kDriver},
                {ActivityProperty{{41}}, PropertySource::kFake},
            },
        },

        FloorActivityData{
            {
                {ActivityProperty{{10}}, PropertySource::kDriver},
            },
            {
                {ActivityProperty{{41}}, PropertySource::kFake},
                {ActivityProperty{{61}}, PropertySource::kFake},
            },
            {0, 40},
            {
                {ActivityProperty{{0}}, PropertySource::kDriver},
                {ActivityProperty{{61}}, PropertySource::kFake},
            },
        },

        FloorActivityData{
            {
                {ActivityProperty{{50}}, PropertySource::kDriver},
            },
            {
                {ActivityProperty{{41}}, PropertySource::kFake},
                {ActivityProperty{{61}}, PropertySource::kFake},
            },
            {41, 60},
            {
                {ActivityProperty{{41}}, PropertySource::kDriver},
                {ActivityProperty{{61}}, PropertySource::kFake},
            },
        },

        FloorActivityData{
            {
                {ActivityProperty{{70}}, PropertySource::kDriver},
            },
            {
                {ActivityProperty{{41}}, PropertySource::kFake},
                {ActivityProperty{{61}}, PropertySource::kFake},
            },
            {61, 100},
            {
                {ActivityProperty{{61}}, PropertySource::kDriver},
            },
        },
    }));
