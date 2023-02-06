#include <gtest/gtest.h>
#include <userver/utils/statistics/percentile.hpp>
#include <userver/utils/statistics/percentile_format_json.hpp>

#include <applicators/cart.hpp>
#include <eats-discounts-applicator/metrics.hpp>
#include <tests/utils.hpp>

namespace eats_discounts_applicator::tests {

namespace {

struct TestParams {
  std::vector<int> timings;
  std::vector<int> expected_timings;
  std::string test_name;
};

class TestMetricPercentile : public testing::TestWithParam<TestParams> {};

std::string PrintToString(const TestParams& params) { return params.test_name; }

const std::vector<TestParams> kBasicTestParams = {
    {
        {
            14,
            10,
            22,
            12,
            123,
            11,
            50,
        },
        {10, 14, 123, 123, 123, 123, 123, 123, 123},
        "percentile_test",
    },
    {
        {
            3,
            5,
            8,
            1,
            7,
            4,
            0,
            10,
            6,
            9,
            2,
        },
        {0, 5, 9, 10, 10, 10, 10, 10, 10},
        "90th_percentile_test",
    },
};

void CheckPercentiles(
    const eats_discounts_applicator::metrics::RecentPeriod& timings,
    const std::vector<int>& expected_timings) {
  const formats::json::Value& stats =
      utils::statistics::PercentileToJson(
          timings.GetStatsForPeriod(
              utils::datetime::SteadyClock::duration::
                  min() /* use whole RecentPeriod range */,
              true /* with_current_epoch */
              ))
          .ExtractValue();
  EXPECT_EQ(formats::json::ToString(stats["p0"]),
            std::to_string(expected_timings[0]));
  EXPECT_EQ(formats::json::ToString(stats["p50"]),
            std::to_string(expected_timings[1]));
  EXPECT_EQ(formats::json::ToString(stats["p90"]),
            std::to_string(expected_timings[2]));
  EXPECT_EQ(formats::json::ToString(stats["p95"]),
            std::to_string(expected_timings[3]));
  EXPECT_EQ(formats::json::ToString(stats["p98"]),
            std::to_string(expected_timings[4]));
  EXPECT_EQ(formats::json::ToString(stats["p99"]),
            std::to_string(expected_timings[5]));
  EXPECT_EQ(formats::json::ToString(stats["p99_6"]),
            std::to_string(expected_timings[6]));
  EXPECT_EQ(formats::json::ToString(stats["p99_9"]),
            std::to_string(expected_timings[7]));
  EXPECT_EQ(formats::json::ToString(stats["p100"]),
            std::to_string(expected_timings[8]));
}

}  // namespace

TEST_P(TestMetricPercentile, BasicTest) {
  const auto& params = GetParam();
  eats_discounts_applicator::metrics::Metrics metrics;
  for (const auto duration : params.timings) {
    metrics.get_discounts_for_cart_timings.GetCurrentCounter().Account(
        duration);
    metrics.get_discounts_for_items_timings.GetCurrentCounter().Account(
        duration);
    metrics.get_places_discounts_timings.GetCurrentCounter().Account(duration);
    metrics.get_cashback_for_items_timings.GetCurrentCounter().Account(
        duration);
    metrics.get_discounts_fetcher_timings.GetCurrentCounter().Account(duration);
  }
  CheckPercentiles(metrics.get_discounts_for_cart_timings,
                   params.expected_timings);
  CheckPercentiles(metrics.get_discounts_for_items_timings,
                   params.expected_timings);
  CheckPercentiles(metrics.get_places_discounts_timings,
                   params.expected_timings);
  CheckPercentiles(metrics.get_cashback_for_items_timings,
                   params.expected_timings);
  CheckPercentiles(metrics.get_discounts_fetcher_timings,
                   params.expected_timings);
}

INSTANTIATE_TEST_SUITE_P(/* no prefix */, TestMetricPercentile,
                         testing::ValuesIn(kBasicTestParams),
                         testing::PrintToStringParamName());

}  // namespace eats_discounts_applicator::tests
