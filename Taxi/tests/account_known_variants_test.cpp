#include <gtest/gtest.h>

#include <logic/fetch_schedule.hpp>
#include <models/test/types.hpp>
#include <optional>

#include "common.hpp"

using namespace subvention_matcher;
using namespace logic::impl;

struct AccountKnownVariantTestData {
  InternalScheduleParameters variant;
  std::vector<test::TestKnownInterval> known;
  std::vector<models::TimeRange> expected_known;
  std::vector<models::TimeRange> expected_unknown;
};

struct AccountKnownVariantTestParametrized
    : public BaseTestWithParam<AccountKnownVariantTestData> {};

TEST_P(AccountKnownVariantTestParametrized, AccountKnownVariant) {
  auto cpy = GetParam().variant;
  for (const auto& k : GetParam().known) {
    AccountKnownVariant(cpy, k);
  }

  CleanEmptyRanges(cpy.known_ranges);
  CleanEmptyRanges(cpy.unknown_ranges);
  ASSERT_EQ(cpy.known_ranges, GetParam().expected_known);
  ASSERT_EQ(cpy.unknown_ranges, GetParam().expected_unknown);
}

// failing case in prod
// known_ranges:
//   [2021-08-03T11:33:47+0000, 2021-08-03T17:00:00+0000),
//   [2021-08-03T17:00:00+0000, 2021-08-07T17:00:00+0000)
// unknown_ranges:
//   [2021-08-03T17:00:00+0000, 2021-08-03T17:00:00+0000)
//   [2021-08-07T17:00:00+0000, 2021-08-08T11:33:47+0000),
INSTANTIATE_TEST_SUITE_P(
    AccountKnownVariantTestParametrized, AccountKnownVariantTestParametrized,
    ::testing::ValuesIn({
        AccountKnownVariantTestData{
            InternalScheduleParameters{
                {},
                GetMskTz(),
                {},
                {
                    {
                        dt::Stringtime("2021-08-03T11:33:47Z"),
                        dt::Stringtime("2021-08-08T11:33:47Z"),
                    },
                },
                {},
                {},
            },
            {
                {
                    dt::Stringtime("2021-08-03T11:33:47Z"),
                    dt::Stringtime("2021-08-03T17:00:00Z"),
                },
                {
                    dt::Stringtime("2021-08-03T17:00:00Z"),
                    dt::Stringtime("2021-08-07T17:00:00Z"),
                },
            },
            {
                {
                    dt::Stringtime("2021-08-03T11:33:47Z"),
                    dt::Stringtime("2021-08-03T17:00:00Z"),
                },
                {
                    dt::Stringtime("2021-08-03T17:00:00Z"),
                    dt::Stringtime("2021-08-07T17:00:00Z"),
                },
            },
            {
                {
                    dt::Stringtime("2021-08-07T17:00:00Z"),
                    dt::Stringtime("2021-08-08T11:33:47Z"),
                },
            },
        },
        {
            InternalScheduleParameters{
                {},
                GetMskTz(),
                {},
                {
                    {
                        dt::Stringtime("2021-08-03T11:33:47Z"),
                        dt::Stringtime("2021-08-07T17:00:00Z"),
                    },
                },
                {},
                {},
            },
            {
                {
                    dt::Stringtime("2021-08-03T11:33:47Z"),
                    dt::Stringtime("2021-08-03T17:00:00Z"),
                },
                {
                    dt::Stringtime("2021-08-03T17:00:00Z"),
                    dt::Stringtime("2021-08-07T17:00:00Z"),
                },
            },
            {
                {
                    dt::Stringtime("2021-08-03T11:33:47Z"),
                    dt::Stringtime("2021-08-03T17:00:00Z"),
                },
                {
                    dt::Stringtime("2021-08-03T17:00:00Z"),
                    dt::Stringtime("2021-08-07T17:00:00Z"),
                },
            },
            {},
        },
        {
            InternalScheduleParameters{
                {},
                GetMskTz(),
                {},
                {
                    {
                        dt::Stringtime("2021-08-03T11:33:47Z"),
                        dt::Stringtime("2021-08-07T17:00:00Z"),
                    },
                },
                {},
                {},
            },
            {
                {
                    dt::Stringtime("2021-08-03T17:00:00Z"),
                    dt::Stringtime("2021-08-07T17:00:00Z"),
                },
                {
                    dt::Stringtime("2021-08-03T11:33:47Z"),
                    dt::Stringtime("2021-08-03T17:00:00Z"),
                },
            },
            {
                {
                    dt::Stringtime("2021-08-03T17:00:00Z"),
                    dt::Stringtime("2021-08-07T17:00:00Z"),
                },
                {
                    dt::Stringtime("2021-08-03T11:33:47Z"),
                    dt::Stringtime("2021-08-03T17:00:00Z"),
                },
            },
            {},
        },
    }));
