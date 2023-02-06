#include <userver/utest/utest.hpp>

#include <userver/formats/json.hpp>

#include <userver/utils/mock_now.hpp>

#include <metrics-aggregations/aggregations.hpp>

namespace {

const std::initializer_list<double> kPercents = {10, 50, 98};

struct DeliveryTimeMetric
    : public metrics_aggregations::PercentileMetricsBase<60 /* kBucketsCount */,
                                                         std::string, int> {
  DeliveryTimeMetric() : Base({"country", "region_id"}, kPercents) {}
};

const std::string kExpectedJson = R"(
{
  "Russia": {
    "213": {
      "p10": 10,
      "p50": 35,
      "p98": 58,
      "$meta": {
        "solomon_children_labels": "percentile"
      }
    },
    "$meta": {
      "solomon_children_labels": "region_id"
    }
  },
  "$meta": {
    "solomon_children_labels": "country"
  }
})";

TEST(TestMetricPercentile, Basic) {
  RunInCoro(
      [] {
        auto now = utils::datetime::Now();

        utils::datetime::MockNowSet(now);

        auto metric = DeliveryTimeMetric{};
        metric.GetCounter("Russia", 213).Account(10);
        metric.GetCounter("Russia", 213).Account(11);
        metric.GetCounter("Russia", 213).Account(30);
        metric.GetCounter("Russia", 213).Account(35);
        metric.GetCounter("Russia", 213).Account(40);
        metric.GetCounter("Russia", 213).Account(41);
        metric.GetCounter("Russia", 213).Account(58);

        utils::datetime::MockSleep(std::chrono::seconds(10));

        ASSERT_EQ(metric.ToJson(), formats::json::FromString(kExpectedJson));
      },
      1);
}

}  // namespace
