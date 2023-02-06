#include <userver/utest/utest.hpp>
#include "metric_reader_mocks.hpp"
#include "types/metric_value.hpp"

namespace eats_report_storage::snapshot {
using namespace ::testing;

static std::pair<std::string, models::ConfigMetricData> MakeMetricFixed(
    const std::string& id, const std::optional<std::string>& unit, int decimals,
    bool inverse, std::string_view column_name, std::string_view table_name,
    bool is_additive) {
  models::ConfigMetricData metric;
  models::MetricsConfig metric_config;
  metric.data_key = id;
  metric.value_unit_sign = unit;
  metric.simbols_after_comma = decimals;
  metric.inverse = inverse;
  metric.type = types::MetricType::kFixed;
  metric.column_name = column_name;
  metric.table_name = table_name;
  metric.is_additive = is_additive;
  return {id, std::move(metric)};
}

static std::pair<std::string, models::ConfigMetricData> MakeMetric(
    const std::string& id, const std::optional<std::string>& unit, int decimals,
    bool inverse) {
  models::ConfigMetricData metric;
  metric.data_key = id;
  metric.value_unit_sign = unit;
  metric.simbols_after_comma = decimals;
  metric.inverse = inverse;
  metric.type = types::MetricType::kCustom;
  return {id, std::move(metric)};
}

struct MetricDefinedWithTypeTest : public Test {
  models::MetricsConfig metrics_config;
  MetricDefinedWithTypeTest() {
    metrics_config.metrics.emplace(MakeMetricFixed("common_order_success_count",
                                                   "₽", 2, true, "colon_one",
                                                   "table_one", true));
    metrics_config.metrics.emplace(MakeMetricFixed("common_order_cancel_count",
                                                   "₽", 2, false, "colon_two",
                                                   "table_two", false));
    metrics_config.metrics.emplace(
        MakeMetric("common_revenue_lost", "₽", 2, true));
    metrics_config.metrics.emplace(
        MakeMetric("common_revenue_earned", "₽", 2, false));
    metrics_config.periods.emplace(
        std::make_pair("week", models::ConfigPeriodData{{"day"}}));
  }
};

TEST_F(MetricDefinedWithTypeTest, Get_fixed_metrics) {
  models::metrics::MetricDefinition definition(metrics_config);
  ASSERT_EQ(definition(types::MetricId{"common_order_success_count"})
                ->GetMetricTable(),
            "table_one");
  ASSERT_EQ(definition(types::MetricId{"common_order_success_count"})
                ->GetMetricField(),
            "colon_one");
}

TEST_F(MetricDefinedWithTypeTest, Get_fixed_metrics_two) {
  models::metrics::MetricDefinition definition(metrics_config);
  ASSERT_EQ(definition(types::MetricId{"common_order_cancel_count"})
                ->GetMetricTable(),
            "table_two");
  ASSERT_EQ(definition(types::MetricId{"common_order_cancel_count"})
                ->GetMetricField(),
            "colon_two");
}

TEST_F(MetricDefinedWithTypeTest, Get_custom_metrics) {
  models::metrics::MetricDefinition definition(metrics_config);
  ASSERT_EQ(
      definition(types::MetricId{"common_revenue_lost"})->GetMetricTable(),
      "eats_report_storage.agg_place_metric");
  ASSERT_EQ(
      definition(types::MetricId{"common_revenue_lost"})->GetMetricField(),
      "revenue_lost_lcy");
}

TEST_F(MetricDefinedWithTypeTest, Get_custom_metrics_two) {
  models::metrics::MetricDefinition definition(metrics_config);
  ASSERT_EQ(
      definition(types::MetricId{"common_revenue_earned"})->GetMetricTable(),
      "eats_report_storage.agg_place_metric");
  ASSERT_EQ(
      definition(types::MetricId{"common_revenue_earned"})->GetMetricField(),
      "revenue_earned_lcy");
}

}  // namespace eats_report_storage::snapshot
