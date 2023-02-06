#include <userver/utest/utest.hpp>

#include <userver/formats/json.hpp>

#include <metrics-aggregations/aggregations.hpp>

namespace {

enum class Status {
  kSuccess,
  kFailed,
};

std::string ToString(Status status) {
  switch (status) {
    case Status::kSuccess:
      return "success";
    case Status::kFailed:
      return "failed";
  }
}

struct DeliveryStatusMetric
    : public metrics_aggregations::CounterMetricsBase<std::string, Status> {
  DeliveryStatusMetric() : Base({"country", "status"}) {}
};

const std::string kExpectedJson = R"(
{
  "Russia": {
    "success": 2,
    "failed": 1,
    "$meta": {
      "solomon_children_labels": "status"
    }
  },
  "$meta": {
    "solomon_children_labels": "country"
  }
})";

TEST(TestMetricCounter, Basic) {
  RunInCoro(
      [] {
        auto metric = DeliveryStatusMetric{};
        metric.GetCounter("Russia", Status::kSuccess).Increment();
        metric.GetCounter("Russia", Status::kSuccess).Increment();
        metric.GetCounter("Russia", Status::kFailed).Increment();

        ASSERT_EQ(metric.ToJson(), formats::json::FromString(kExpectedJson));
      },
      1);
}

}  // namespace
