#include <optional>
#include <set>

#include <gtest/gtest.h>

#include "common.hpp"

#include <db/types.hpp>
#include <logic/common.hpp>
#include <logic/fetch_schedule.hpp>
#include <models/types.hpp>

using namespace logic;
using namespace logic::impl;

struct RangeData {
  cctz::time_zone tz;
  models::TimeRange range;
  std::vector<models::TimeRange> expected_ranges;
};

struct RangeDataTestParametrized : public BaseTestWithParam<RangeData> {};

TEST_P(RangeDataTestParametrized, Test) {
  const auto& ranges = SplitByWeek(GetParam().range, GetParam().tz);
  ASSERT_EQ(ranges, GetParam().expected_ranges);
}

INSTANTIATE_TEST_SUITE_P(RangeDataTestParametrized, RangeDataTestParametrized,
                         ::testing::ValuesIn({
                             RangeData{
                                 GetMskTz(),
                                 {
                                     dt::Stringtime("2021-02-01T00:00:00Z"),
                                     dt::Stringtime("2021-02-06T00:00:00Z"),
                                 },
                                 {
                                     {
                                         dt::Stringtime("2021-02-01T00:00:00Z"),
                                         dt::Stringtime("2021-02-06T00:00:00Z"),
                                     },
                                 },
                             },
                             RangeData{
                                 GetMskTz(),
                                 {
                                     dt::Stringtime("2021-02-02T00:00:00Z"),
                                     dt::Stringtime("2021-02-09T00:00:00Z"),
                                 },
                                 {
                                     {
                                         dt::Stringtime("2021-02-02T00:00:00Z"),
                                         dt::Stringtime("2021-02-07T21:00:00Z"),
                                     },
                                     {
                                         dt::Stringtime("2021-02-07T21:00:00Z"),
                                         dt::Stringtime("2021-02-09T00:00:00Z"),
                                     },
                                 },
                             },
                         }));

struct GetUnknownIntervalsData {
  FetchScheduleContext ctx;
  std::vector<db::DescriptorWithItems> known;
  std::vector<InternalScheduleParameters> expected;
};

struct GetUnknownIntervalsTestParametrized
    : public BaseTestWithParam<GetUnknownIntervalsData> {};

TEST_P(GetUnknownIntervalsTestParametrized, Test) {
  auto ctx = GetParam().ctx;
  auto& known = GetParam().known;
  UpdateUnknownIntervals(ctx, known);

  ASSERT_EQ(ctx.variants, GetParam().expected);
}

static const models::ScheduleParameters kDefaultDescriptor{
    "moscow",
    "eco",
    models::RuleType::kSingleRide,
};

INSTANTIATE_TEST_SUITE_P(
    GetUnknownIntervalsTestParametrized, GetUnknownIntervalsTestParametrized,
    ::testing::ValuesIn({
        // 0
        GetUnknownIntervalsData{
            FetchScheduleContext{
                {
                    InternalScheduleParameters{
                        kDefaultDescriptor,
                        GetMskTz(),
                        {},
                        {
                            {
                                dt::Stringtime("2021-02-01T00:00:00Z"),
                                dt::Stringtime("2021-02-06T00:00:00Z"),
                            },
                        },
                        {},
                        {},
                    },
                },
                models::FetchParameters{
                    {
                        dt::Stringtime("2021-02-01T00:00:00Z"),
                        dt::Stringtime("2021-02-06T00:00:00Z"),
                    },
                    {},
                    0,
                    models::Branding::kSticker | models::Branding::kLightbox,
                    {"tag"},
                },
                {},
            },
            {
                db::DescriptorWithItems{
                    models::RuleType::kSingleRide,
                    "moscow",
                    "eco",
                    dt::Stringtime("2021-02-01T00:00:00Z"),
                    dt::Stringtime("2021-02-06T00:00:00Z"),
                    {},
                },
            },
            {
                InternalScheduleParameters{
                    kDefaultDescriptor,
                    GetMskTz(),
                    {
                        {
                            dt::Stringtime("2021-02-01T00:00:00Z"),
                            dt::Stringtime("2021-02-06T00:00:00Z"),
                        },
                    },
                    {},
                    {},
                    {},
                },
            },
        },

        // 1
        GetUnknownIntervalsData{
            FetchScheduleContext{
                {
                    InternalScheduleParameters{
                        kDefaultDescriptor,
                        GetMskTz(),
                        {},
                        {
                            {
                                dt::Stringtime("2021-02-01T00:00:00Z"),
                                dt::Stringtime("2021-02-06T00:00:00Z"),
                            },
                        },
                        {},
                        {},
                    },
                },
                models::FetchParameters{
                    {
                        dt::Stringtime("2021-02-01T00:00:00Z"),
                        dt::Stringtime("2021-02-06T00:00:00Z"),
                    },
                    {},
                    0,
                    models::Branding::kSticker | models::Branding::kLightbox,
                    {"tag"},
                },
                {},
            },
            {
                db::DescriptorWithItems{
                    models::RuleType::kSingleRide,
                    "moscow",
                    "eco",
                    dt::Stringtime("2021-02-02T00:00:00Z"),
                    dt::Stringtime("2021-02-03T00:00:00Z"),
                    {},
                },
            },
            {
                InternalScheduleParameters{
                    kDefaultDescriptor,
                    GetMskTz(),
                    {
                        {
                            dt::Stringtime("2021-02-02T00:00:00Z"),
                            dt::Stringtime("2021-02-03T00:00:00Z"),
                        },
                    },
                    {
                        {
                            dt::Stringtime("2021-02-01T00:00:00Z"),
                            dt::Stringtime("2021-02-02T00:00:00Z"),
                        },
                        {
                            dt::Stringtime("2021-02-03T00:00:00Z"),
                            dt::Stringtime("2021-02-06T00:00:00Z"),
                        },
                    },
                    {},
                    {},
                },
            },
        },

        // 2
        GetUnknownIntervalsData{
            FetchScheduleContext{
                {
                    InternalScheduleParameters{
                        kDefaultDescriptor,
                        GetMskTz(),
                        {},
                        {
                            {
                                dt::Stringtime("2021-02-01T00:00:00Z"),
                                dt::Stringtime("2021-02-03T00:00:00Z"),
                            },
                        },
                        {},
                        {},
                    },
                },
                models::FetchParameters{
                    {
                        dt::Stringtime("2021-02-01T00:00:00Z"),
                        dt::Stringtime("2021-02-03T00:00:00Z"),
                    },
                    {},
                    0,
                    models::Branding::kSticker | models::Branding::kLightbox,
                    {"tag"},
                },
                {},
            },
            {
                db::DescriptorWithItems{
                    models::RuleType::kSingleRide,
                    "moscow",
                    "eco",
                    dt::Stringtime("2021-02-02T00:00:00Z"),
                    dt::Stringtime("2021-02-05T00:00:00Z"),
                    {},
                },
            },
            {
                InternalScheduleParameters{
                    kDefaultDescriptor,
                    GetMskTz(),
                    {
                        {
                            dt::Stringtime("2021-02-02T00:00:00Z"),
                            dt::Stringtime("2021-02-03T00:00:00Z"),
                        },
                    },
                    {
                        {
                            dt::Stringtime("2021-02-01T00:00:00Z"),
                            dt::Stringtime("2021-02-02T00:00:00Z"),
                        },
                    },
                    {},
                    {},
                },
            },
        },

        // 3
        GetUnknownIntervalsData{
            FetchScheduleContext{
                {
                    InternalScheduleParameters{
                        kDefaultDescriptor,
                        GetMskTz(),
                        {},
                        {
                            {
                                dt::Stringtime("2021-02-03T00:00:00Z"),
                                dt::Stringtime("2021-02-07T00:00:00Z"),
                            },
                        },
                        {},
                        {},
                    },
                },
                models::FetchParameters{
                    {
                        dt::Stringtime("2021-02-03T00:00:00Z"),
                        dt::Stringtime("2021-02-07T00:00:00Z"),
                    },
                    {},
                    0,
                    models::Branding::kSticker | models::Branding::kLightbox,
                    {"tag"},
                },
                {},
            },
            {
                db::DescriptorWithItems{
                    models::RuleType::kSingleRide,
                    "moscow",
                    "eco",
                    dt::Stringtime("2021-02-02T00:00:00Z"),
                    dt::Stringtime("2021-02-05T00:00:00Z"),
                    {},
                },
            },
            {
                InternalScheduleParameters{
                    kDefaultDescriptor,
                    GetMskTz(),
                    {
                        {
                            dt::Stringtime("2021-02-03T00:00:00Z"),
                            dt::Stringtime("2021-02-05T00:00:00Z"),
                        },
                    },
                    {
                        {
                            dt::Stringtime("2021-02-05T00:00:00Z"),
                            dt::Stringtime("2021-02-07T00:00:00Z"),
                        },
                    },
                    {},
                    {},
                },
            },
        },

        // 4
        GetUnknownIntervalsData{
            FetchScheduleContext{
                {
                    InternalScheduleParameters{
                        kDefaultDescriptor,
                        GetMskTz(),
                        {},
                        {
                            {
                                dt::Stringtime("2021-02-01T00:00:00Z"),
                                dt::Stringtime("2021-02-07T00:00:00Z"),
                            },
                        },
                        {},
                        {},
                    },
                },
                models::FetchParameters{
                    {
                        dt::Stringtime("2021-02-01T00:00:00Z"),
                        dt::Stringtime("2021-02-07T00:00:00Z"),
                    },
                    {},
                    0,
                    models::Branding::kSticker | models::Branding::kLightbox,
                    {"tag"},
                },
                {},
            },
            {
                db::DescriptorWithItems{
                    models::RuleType::kSingleRide,
                    "moscow",
                    "eco",
                    dt::Stringtime("2021-02-02T00:00:00Z"),
                    dt::Stringtime("2021-02-03T00:00:00Z"),
                    {},
                },
                db::DescriptorWithItems{
                    models::RuleType::kSingleRide,
                    "moscow",
                    "eco",
                    dt::Stringtime("2021-02-04T00:00:00Z"),
                    dt::Stringtime("2021-02-05T00:00:00Z"),
                    {},
                },
            },
            {
                InternalScheduleParameters{
                    kDefaultDescriptor,
                    GetMskTz(),
                    {
                        {
                            dt::Stringtime("2021-02-02T00:00:00Z"),
                            dt::Stringtime("2021-02-03T00:00:00Z"),
                        },
                        {
                            dt::Stringtime("2021-02-04T00:00:00Z"),
                            dt::Stringtime("2021-02-05T00:00:00Z"),
                        },
                    },
                    {
                        {
                            dt::Stringtime("2021-02-01T00:00:00Z"),
                            dt::Stringtime("2021-02-02T00:00:00Z"),
                        },
                        {
                            dt::Stringtime("2021-02-03T00:00:00Z"),
                            dt::Stringtime("2021-02-04T00:00:00Z"),
                        },
                        {
                            dt::Stringtime("2021-02-05T00:00:00Z"),
                            dt::Stringtime("2021-02-07T00:00:00Z"),
                        },
                    },
                    {},
                    {},
                },
            },
        },

        // 5
        GetUnknownIntervalsData{
            FetchScheduleContext{
                {
                    InternalScheduleParameters{
                        kDefaultDescriptor,
                        GetMskTz(),
                        {},
                        {
                            {
                                dt::Stringtime("2021-02-01T09:00:00Z"),
                                dt::Stringtime("2021-02-07T21:00:00Z"),
                            },
                            {
                                dt::Stringtime("2021-02-07T21:00:00Z"),
                                dt::Stringtime("2021-02-14T21:00:00Z"),
                            },
                            {
                                dt::Stringtime("2021-02-14T21:00:00Z"),
                                dt::Stringtime("2021-02-21T21:00:00Z"),
                            },
                            {
                                dt::Stringtime("2021-02-21T21:00:00Z"),
                                dt::Stringtime("2021-02-28T21:00:00Z"),
                            },
                            {
                                dt::Stringtime("2021-02-28T21:00:00Z"),
                                dt::Stringtime("2021-03-07T21:00:00Z"),
                            },
                            {
                                dt::Stringtime("2021-03-07T21:00:00Z"),
                                dt::Stringtime("2021-03-11T09:00:00Z"),
                            },
                        },
                        {},
                        {},
                    },
                },
                models::FetchParameters{
                    {
                        dt::Stringtime("2021-01-31T21:00:00Z"),
                        dt::Stringtime("2021-03-10T21:00:00Z"),
                    },
                    {},
                    0,
                    models::Branding::kSticker | models::Branding::kLightbox,
                    {"tag"},
                },
                {},
            },
            {
                db::DescriptorWithItems{
                    models::RuleType::kSingleRide,
                    "moscow",
                    "eco",
                    dt::Stringtime("2021-01-31T21:00:00Z"),
                    dt::Stringtime("2021-03-10T21:00:00Z"),
                    {},
                },
            },
            {
                InternalScheduleParameters{
                    kDefaultDescriptor,
                    GetMskTz(),
                    {
                        {
                            dt::Stringtime("2021-02-01T09:00:00Z"),
                            dt::Stringtime("2021-02-07T21:00:00Z"),
                        },
                        {
                            dt::Stringtime("2021-02-07T21:00:00Z"),
                            dt::Stringtime("2021-02-14T21:00:00Z"),
                        },
                        {
                            dt::Stringtime("2021-02-14T21:00:00Z"),
                            dt::Stringtime("2021-02-21T21:00:00Z"),
                        },
                        {
                            dt::Stringtime("2021-02-21T21:00:00Z"),
                            dt::Stringtime("2021-02-28T21:00:00Z"),
                        },
                        {
                            dt::Stringtime("2021-02-28T21:00:00Z"),
                            dt::Stringtime("2021-03-07T21:00:00Z"),
                        },
                        {
                            dt::Stringtime("2021-03-07T21:00:00Z"),
                            dt::Stringtime("2021-03-10T21:00:00Z"),
                        },
                    },
                    {
                        {
                            dt::Stringtime("2021-03-10T21:00:00Z"),
                            dt::Stringtime("2021-03-11T09:00:00Z"),
                        },
                    },
                    {},
                    {},
                },
            },
        },
    }));

struct FilterRangesData {
  std::set<TimeRangeWithMask> ranges;
  std::vector<models::TimeRange> original;
  std::set<TimeRangeWithMask> expected;
};

struct FilterRangesTestParametrized
    : public BaseTestWithParam<FilterRangesData> {};

TEST_P(FilterRangesTestParametrized, Test) {
  auto ranges = GetParam().ranges;
  FilterRanges(ranges, GetParam().original);
  ASSERT_EQ(ranges, GetParam().expected);
}

INSTANTIATE_TEST_SUITE_P(
    FilterRangesTestParametrized, FilterRangesTestParametrized,
    ::testing::ValuesIn({

        FilterRangesData{
            {
                TimeRangeWithMask(dt::Stringtime("2021-02-02T00:00:00Z"),
                                  dt::Stringtime("2021-02-03T00:00:00Z")),
            },
            {
                {
                    dt::Stringtime("2021-02-02T00:00:00Z"),
                    dt::Stringtime("2021-02-03T00:00:00Z"),
                },
            },
            {
                TimeRangeWithMask(dt::Stringtime("2021-02-02T00:00:00Z"),
                                  dt::Stringtime("2021-02-03T00:00:00Z")),
            },
        },

        FilterRangesData{
            {
                TimeRangeWithMask(dt::Stringtime("2021-02-02T00:00:00Z"),
                                  dt::Stringtime("2021-02-03T00:00:00Z")),
                TimeRangeWithMask(dt::Stringtime("2021-02-05T00:00:00Z"),
                                  dt::Stringtime("2021-02-06T00:00:00Z")),
            },
            {
                {
                    dt::Stringtime("2021-02-02T00:00:00Z"),
                    dt::Stringtime("2021-02-03T00:00:00Z"),
                },
            },
            {
                TimeRangeWithMask(dt::Stringtime("2021-02-02T00:00:00Z"),
                                  dt::Stringtime("2021-02-03T00:00:00Z")),
            },
        },

        FilterRangesData{
            {
                TimeRangeWithMask(dt::Stringtime("2021-02-02T00:00:00Z"),
                                  dt::Stringtime("2021-02-04T00:00:00Z")),
            },
            {
                {
                    dt::Stringtime("2021-02-03T00:00:00Z"),
                    dt::Stringtime("2021-02-05T00:00:00Z"),
                },
            },
            {
                TimeRangeWithMask(dt::Stringtime("2021-02-02T00:00:00Z"),
                                  dt::Stringtime("2021-02-04T00:00:00Z")),
            },
        },

        FilterRangesData{
            {
                TimeRangeWithMask(dt::Stringtime("2021-02-02T00:00:00Z"),
                                  dt::Stringtime("2021-02-04T00:00:00Z")),
            },
            {
                {
                    dt::Stringtime("2021-02-01T00:00:00Z"),
                    dt::Stringtime("2021-02-03T00:00:00Z"),
                },
            },
            {
                TimeRangeWithMask(dt::Stringtime("2021-02-02T00:00:00Z"),
                                  dt::Stringtime("2021-02-04T00:00:00Z")),
            },
        },

        FilterRangesData{
            {
                TimeRangeWithMask(dt::Stringtime("2021-02-02T00:00:00Z"),
                                  dt::Stringtime("2021-02-04T00:00:00Z")),
            },
            {
                {
                    dt::Stringtime("2021-02-01T00:00:00Z"),
                    dt::Stringtime("2021-02-02T00:00:00Z"),
                },
            },
            {},
        },

    }));
