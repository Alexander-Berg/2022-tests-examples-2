#pragma once

#include <gmock/gmock.h>
#include <models/metrics/metrics_definitions/metrics_definitions.hpp>
#include <userver/utest/utest.hpp>

namespace eats_report_storage::testing {

struct MetricReaderMock : public models::metrics::MetricReader {
  MOCK_METHOD(types::PeriodPoints, GetData,
              (const storages::postgres::ClusterPtr&, const types::Period&,
               const types::PlaceIds&),
              (const, override));
  MOCK_METHOD(std::optional<double>, GetTotalValue,
              (const storages::postgres::ClusterPtr&, const types::Period&,
               const types::PlaceIds&),
              (const, override));
  MOCK_METHOD(std::optional<double>, GetPrevTotalValue,
              (const storages::postgres::ClusterPtr&, const types::Period&,
               const types::PlaceIds&),
              (const, override));

  std::string GetMetricField() const override { return "field"; }
  std::string GetMetricTable() const override { return "table"; }
};

#define MOCK_METRIC_READER(name, id)               \
  struct name##_ : public MetricReaderMock {       \
    types::MetricId GetMetricId() const override { \
      return types::MetricId{id};                  \
    }                                              \
  };                                               \
  using name = ::testing::StrictMock<name##_>;

MOCK_METRIC_READER(CommonRevenueEarnedMock, "common_revenue_earned");
MOCK_METRIC_READER(CommonRevenueLostMock, "common_revenue_lost");
MOCK_METRIC_READER(CommonOrderCountMock, "common_order_count");

#undef MOCK_METRIC_READER

struct MetricDefinitionMock : public models::metrics::BaseMetricDefinition {
  std::shared_ptr<CommonRevenueEarnedMock> common_revenue_earned_mock =
      std::make_shared<CommonRevenueEarnedMock>();
  std::shared_ptr<CommonRevenueLostMock> common_revenue_lost_mock =
      std::make_shared<CommonRevenueLostMock>();
  std::shared_ptr<CommonOrderCountMock> common_order_count_mock =
      std::make_shared<CommonOrderCountMock>();

  explicit MetricDefinitionMock(models::MetricsConfig& config)
      : models::metrics::BaseMetricDefinition(config) {}

  std::shared_ptr<models::metrics::MetricReader> operator()(
      types::MetricId metric_id) const override final {
    if (metric_id == types::metric_id::kCommonRevenueEarned)
      return common_revenue_earned_mock;
    else if (metric_id == types::metric_id::kCommonRevenueLost)
      return common_revenue_lost_mock;
    else if (metric_id == types::metric_id::kCommonOrderCount)
      return common_order_count_mock;
    return {};
  }
};

}  // namespace eats_report_storage::testing
