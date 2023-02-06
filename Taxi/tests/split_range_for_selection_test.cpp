#include <userver/utest/utest.hpp>

#include <algorithm>

#include <userver/utils/datetime.hpp>

#include <db/datetime/split_range_for_selection.hpp>

namespace {

namespace dms = driver_metrics_storage;
using dms::datetime::AggregatedRange;
using dms::datetime::Range;

using utils::datetime::Stringtime;

struct BasicTestParam {
  std::string testname{};
  Range total_range;
  Range aggregated_range;
  std::vector<AggregatedRange> expected;
};

std::string PrintOperationArgsParam(
    const ::testing::TestParamInfo<BasicTestParam>& param) {
  return param.param.testname;
}

}  // namespace

class DbAggregatorsSuite : public ::testing::TestWithParam<BasicTestParam> {};

INSTANTIATE_UTEST_SUITE_P(
    /**/, DbAggregatorsSuite,
    ::testing::Values(
        BasicTestParam{
            "outside_full",
            Range{
                Stringtime("2021-12-01T10:00:00+0000"),
                Stringtime("2021-12-31T10:00:00+0000"),
            },
            Range{
                Stringtime("2021-12-02T00:00:00+0000"),
                Stringtime("2021-12-21T21:00:00+0000"),
            },
            std::vector<AggregatedRange>{
                AggregatedRange{
                    std::nullopt,
                    Range{
                        Stringtime("2021-12-01T10:00:00+0000"),
                        Stringtime("2021-12-02T00:00:00+0000"),
                    },
                },
                AggregatedRange{
                    "aggregated_table",
                    Range{
                        Stringtime("2021-12-02T00:00:00+0000"),
                        Stringtime("2021-12-21T21:00:00+0000"),
                    },
                },
                AggregatedRange{
                    std::nullopt,
                    Range{
                        Stringtime("2021-12-21T21:00:00+0000"),
                        Stringtime("2021-12-31T10:00:00+0000"),
                    },
                },
            },
        },

        BasicTestParam{
            "lhs_border",
            Range{
                Stringtime("2021-12-02T00:00:00+0000"),
                Stringtime("2021-12-31T10:00:00+0000"),
            },
            Range{
                Stringtime("2021-12-02T00:00:00+0000"),
                Stringtime("2021-12-21T21:00:00+0000"),
            },
            std::vector<AggregatedRange>{
                AggregatedRange{
                    "aggregated_table",
                    Range{
                        Stringtime("2021-12-02T00:00:00+0000"),
                        Stringtime("2021-12-21T21:00:00+0000"),
                    },
                },
                AggregatedRange{
                    std::nullopt,
                    Range{
                        Stringtime("2021-12-21T21:00:00+0000"),
                        Stringtime("2021-12-31T10:00:00+0000"),
                    },
                },
            },
        },

        BasicTestParam{
            "rhs_border",
            Range{
                Stringtime("2021-12-01T10:00:00+0000"),
                Stringtime("2021-12-31T10:00:00+0000"),
            },
            Range{
                Stringtime("2021-12-02T00:00:00+0000"),
                Stringtime("2021-12-31T10:00:00+0000"),
            },
            std::vector<AggregatedRange>{
                AggregatedRange{
                    std::nullopt,
                    Range{
                        Stringtime("2021-12-01T10:00:00+0000"),
                        Stringtime("2021-12-02T00:00:00+0000"),
                    },
                },
                AggregatedRange{
                    "aggregated_table",
                    Range{
                        Stringtime("2021-12-02T00:00:00+0000"),
                        Stringtime("2021-12-31T10:00:00+0000"),
                    },
                },
            },
        },

        BasicTestParam{
            "exact",
            Range{
                Stringtime("2021-12-01T10:00:00+0000"),
                Stringtime("2021-12-31T10:00:00+0000"),
            },
            Range{
                Stringtime("2021-12-01T10:00:00+0000"),
                Stringtime("2021-12-31T10:00:00+0000"),
            },
            std::vector<AggregatedRange>{
                AggregatedRange{
                    "aggregated_table",
                    Range{
                        Stringtime("2021-12-01T10:00:00+0000"),
                        Stringtime("2021-12-31T10:00:00+0000"),
                    },
                },
            },
        }  //
        ),
    PrintOperationArgsParam);

UTEST_P(DbAggregatorsSuite, RunTest) {
  const auto& param = GetParam();

  const auto result = dms::datetime::SplitRangeForSelection(
      param.total_range, "aggregated_table", param.aggregated_range);

  ASSERT_EQ(result, param.expected);
}
