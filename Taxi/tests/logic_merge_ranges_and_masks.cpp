#include <gtest/gtest.h>

#include <boost/range/adaptor/transformed.hpp>

#include "common.hpp"

#include <set>

#include <userver/engine/run_in_coro.hpp>
#include <userver/logging/log.hpp>

#include <logic/fetch_schedule.hpp>
#include <models/types.hpp>

using namespace logic;
using namespace logic::impl;

namespace logic::impl {

inline std::ostream& operator<<(std::ostream& os,
                                const TimeRangeWithMask& data) {
  os << (models::TimeRange)data;
  if (data.mask) {
    return os << ", " << boost::algorithm::join(*data.mask, ", ");
  }
  return os << ", --";
}

inline bool operator==(const TimeRangeWithMask& lhs,
                       const TimeRangeWithMask& rhs) {
  return std::tie(lhs.from, lhs.to, lhs.mask) ==
         std::tie(rhs.from, rhs.to, rhs.mask);
}

}  // namespace logic::impl

struct MergeRangesAndMasksData {
  std::vector<models::TimeRange> week_ranges;
  std::vector<db::MaskInfo> masks;
  std::set<TimeRangeWithMask> expected;
};

struct MergeRangesAndMasksTestParametrized
    : public BaseTestWithParam<MergeRangesAndMasksData> {};

TEST_P(MergeRangesAndMasksTestParametrized, Test) {
  const auto& ranges =
      MergeRangesAndMasks(GetParam().week_ranges, GetParam().masks);
  ASSERT_EQ(ranges, GetParam().expected);
}

db::MaskInfo CreateMask(models::TimePoint from, models::TimePoint to,
                        std::vector<std::string> mask) {
  db::MaskInfo result;

  result.active_from = std::move(from);
  result.active_to = std::move(to);
  result.tags = std::move(mask);

  return result;
}

INSTANTIATE_TEST_SUITE_P(
    MergeRangesAndMasksTestParametrized, MergeRangesAndMasksTestParametrized,
    ::testing::ValuesIn({
        MergeRangesAndMasksData{
            {
                {
                    dt::Stringtime("2021-02-01T00:00:00Z"),
                    dt::Stringtime("2021-02-06T00:00:00Z"),
                },
            },
            {},
            {
                TimeRangeWithMask(dt::Stringtime("2021-02-01T00:00:00Z"),
                                  dt::Stringtime("2021-02-06T00:00:00Z")),
            },
        },
        MergeRangesAndMasksData{
            {
                {
                    dt::Stringtime("2021-02-01T00:00:00Z"),
                    dt::Stringtime("2021-02-06T00:00:00Z"),
                },
                {
                    dt::Stringtime("2021-02-06T00:00:00Z"),
                    dt::Stringtime("2021-02-09T00:00:00Z"),
                },
            },
            {},
            {
                TimeRangeWithMask(dt::Stringtime("2021-02-01T00:00:00Z"),
                                  dt::Stringtime("2021-02-06T00:00:00Z")),
                TimeRangeWithMask(dt::Stringtime("2021-02-06T00:00:00Z"),
                                  dt::Stringtime("2021-02-09T00:00:00Z")),
            },
        },

        MergeRangesAndMasksData{
            {
                {
                    dt::Stringtime("2021-02-01T00:00:00Z"),
                    dt::Stringtime("2021-02-06T00:00:00Z"),
                },
            },
            {
                CreateMask(dt::Stringtime("2021-02-01T00:00:00Z"),
                           dt::Stringtime("2021-02-03T00:00:00Z"), {"t1"}),
            },
            {
                TimeRangeWithMask(dt::Stringtime("2021-02-01T00:00:00Z"),
                                  dt::Stringtime("2021-02-03T00:00:00Z"),
                                  {"t1"}),
                TimeRangeWithMask(dt::Stringtime("2021-02-03T00:00:00Z"),
                                  dt::Stringtime("2021-02-06T00:00:00Z")),
            },
        },

        MergeRangesAndMasksData{
            {
                {
                    dt::Stringtime("2021-02-01T00:00:00Z"),
                    dt::Stringtime("2021-02-06T00:00:00Z"),
                },
                {
                    dt::Stringtime("2021-02-06T00:00:00Z"),
                    dt::Stringtime("2021-02-09T00:00:00Z"),
                },
            },
            {
                CreateMask(dt::Stringtime("2021-02-01T00:00:00Z"),
                           dt::Stringtime("2021-02-03T00:00:00Z"), {"t1"}),
            },
            {
                TimeRangeWithMask(dt::Stringtime("2021-02-01T00:00:00Z"),
                                  dt::Stringtime("2021-02-03T00:00:00Z"),
                                  {"t1"}),
                TimeRangeWithMask(dt::Stringtime("2021-02-03T00:00:00Z"),
                                  dt::Stringtime("2021-02-06T00:00:00Z")),
                TimeRangeWithMask(dt::Stringtime("2021-02-06T00:00:00Z"),
                                  dt::Stringtime("2021-02-09T00:00:00Z")),
            },
        },

        MergeRangesAndMasksData{
            {
                {
                    dt::Stringtime("2021-02-01T00:00:00Z"),
                    dt::Stringtime("2021-02-06T00:00:00Z"),
                },
            },
            {
                CreateMask(dt::Stringtime("2021-02-01T00:00:00Z"),
                           dt::Stringtime("2021-02-06T00:00:00Z"), {"t1"}),
            },
            {
                TimeRangeWithMask(dt::Stringtime("2021-02-01T00:00:00Z"),
                                  dt::Stringtime("2021-02-06T00:00:00Z"),
                                  {"t1"}),
            },
        },

        MergeRangesAndMasksData{
            {
                {
                    dt::Stringtime("2021-02-01T00:00:00Z"),
                    dt::Stringtime("2021-02-06T00:00:00Z"),
                },
            },
            {
                CreateMask(dt::Stringtime("2021-02-01T00:00:00Z"),
                           dt::Stringtime("2021-02-16T00:00:00Z"), {"t1"}),
            },
            {
                TimeRangeWithMask(dt::Stringtime("2021-02-01T00:00:00Z"),
                                  dt::Stringtime("2021-02-06T00:00:00Z"),
                                  {"t1"}),
            },
        },

        MergeRangesAndMasksData{
            {
                {
                    dt::Stringtime("2021-02-01T00:00:00Z"),
                    dt::Stringtime("2021-02-06T00:00:00Z"),
                },
            },
            {
                CreateMask(dt::Stringtime("2021-01-01T00:00:00Z"),
                           dt::Stringtime("2021-02-06T00:00:00Z"), {"t1"}),
            },
            {
                TimeRangeWithMask(dt::Stringtime("2021-02-01T00:00:00Z"),
                                  dt::Stringtime("2021-02-06T00:00:00Z"),
                                  {"t1"}),
            },
        },

        MergeRangesAndMasksData{
            {
                {
                    dt::Stringtime("2021-02-01T00:00:00Z"),
                    dt::Stringtime("2021-02-06T00:00:00Z"),
                },
            },
            {
                CreateMask(dt::Stringtime("2021-01-01T00:00:00Z"),
                           dt::Stringtime("2021-02-16T00:00:00Z"), {"t1"}),
            },
            {
                TimeRangeWithMask(dt::Stringtime("2021-02-01T00:00:00Z"),
                                  dt::Stringtime("2021-02-06T00:00:00Z"),
                                  {"t1"}),
            },
        },

        MergeRangesAndMasksData{
            {
                {
                    dt::Stringtime("2021-02-01T00:00:00Z"),
                    dt::Stringtime("2021-02-03T00:00:00Z"),
                },
                {
                    dt::Stringtime("2021-02-03T00:00:00Z"),
                    dt::Stringtime("2021-02-06T00:00:00Z"),
                },
            },
            {
                CreateMask(dt::Stringtime("2021-02-01T00:00:00Z"),
                           dt::Stringtime("2021-02-06T00:00:00Z"), {"t1"}),
            },
            {
                TimeRangeWithMask(dt::Stringtime("2021-02-01T00:00:00Z"),
                                  dt::Stringtime("2021-02-03T00:00:00Z"),
                                  {"t1"}),
                TimeRangeWithMask(dt::Stringtime("2021-02-03T00:00:00Z"),
                                  dt::Stringtime("2021-02-06T00:00:00Z"),
                                  {"t1"}),
            },
        },

        MergeRangesAndMasksData{
            {
                {
                    dt::Stringtime("2021-02-01T00:00:00Z"),
                    dt::Stringtime("2021-02-06T00:00:00Z"),
                },
            },
            {
                CreateMask(dt::Stringtime("2021-02-01T00:00:00Z"),
                           dt::Stringtime("2021-02-03T00:00:00Z"), {"t1"}),
                CreateMask(dt::Stringtime("2021-02-03T00:00:00Z"),
                           dt::Stringtime("2021-02-06T00:00:00Z"), {"t2"}),
            },
            {
                TimeRangeWithMask(dt::Stringtime("2021-02-01T00:00:00Z"),
                                  dt::Stringtime("2021-02-03T00:00:00Z"),
                                  {"t1"}),
                TimeRangeWithMask(dt::Stringtime("2021-02-03T00:00:00Z"),
                                  dt::Stringtime("2021-02-06T00:00:00Z"),
                                  {"t2"}),
            },
        },

        MergeRangesAndMasksData{
            {
                {
                    dt::Stringtime("2021-02-01T00:00:00Z"),
                    dt::Stringtime("2021-02-06T00:00:00Z"),
                },
                {
                    dt::Stringtime("2021-02-06T00:00:00Z"),
                    dt::Stringtime("2021-02-09T00:00:00Z"),
                },
                {
                    dt::Stringtime("2021-02-09T00:00:00Z"),
                    dt::Stringtime("2021-02-12T00:00:00Z"),
                },
                {
                    dt::Stringtime("2021-02-12T00:00:00Z"),
                    dt::Stringtime("2021-02-15T00:00:00Z"),
                },
            },
            {
                CreateMask(dt::Stringtime("2021-02-01T00:00:00Z"),
                           dt::Stringtime("2021-02-03T00:00:00Z"), {"t1"}),
                CreateMask(dt::Stringtime("2021-02-03T00:00:00Z"),
                           dt::Stringtime("2021-02-08T00:00:00Z"), {"t2"}),
                CreateMask(dt::Stringtime("2021-02-08T00:00:00Z"),
                           dt::Stringtime("2021-02-16T00:00:00Z"), {"t3"}),
            },
            {
                TimeRangeWithMask(dt::Stringtime("2021-02-01T00:00:00Z"),
                                  dt::Stringtime("2021-02-03T00:00:00Z"),
                                  {"t1"}),
                TimeRangeWithMask(dt::Stringtime("2021-02-03T00:00:00Z"),
                                  dt::Stringtime("2021-02-06T00:00:00Z"),
                                  {"t2"}),
                TimeRangeWithMask(dt::Stringtime("2021-02-06T00:00:00Z"),
                                  dt::Stringtime("2021-02-08T00:00:00Z"),
                                  {"t2"}),
                TimeRangeWithMask(dt::Stringtime("2021-02-08T00:00:00Z"),
                                  dt::Stringtime("2021-02-09T00:00:00Z"),
                                  {"t3"}),
                TimeRangeWithMask(dt::Stringtime("2021-02-09T00:00:00Z"),
                                  dt::Stringtime("2021-02-12T00:00:00Z"),
                                  {"t3"}),
                TimeRangeWithMask(dt::Stringtime("2021-02-12T00:00:00Z"),
                                  dt::Stringtime("2021-02-15T00:00:00Z"),
                                  {"t3"}),
            },
        },
    }));
