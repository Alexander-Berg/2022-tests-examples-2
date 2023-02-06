#include <clients/eats-place-rating/client_gmock.hpp>
#include <components/snapshot/metric_snapshot.hpp>
#include <memory>
#include <userver/utest/utest.hpp>
#include "metric_reader_mocks.hpp"
#include "types/metric_value.hpp"

namespace eats_report_storage::types {
inline bool operator==(const MetricValue& lhs, const MetricValue& rhs) {
  return std::make_tuple(lhs.total_value, lhs.delta, lhs.current,
                         lhs.total_value_str, lhs.delta_str, lhs.current_str) ==
         std::make_tuple(rhs.total_value, rhs.delta, rhs.current,
                         rhs.total_value_str, rhs.delta_str, rhs.current_str);
}
}  // namespace eats_report_storage::types

namespace eats_report_storage::snapshot {
using namespace ::testing;

static std::pair<std::string, models::ConfigMetricData> MakeMetric(
    const std::string& id, const std::optional<std::string>& unit, int decimals,
    bool inverse) {
  models::ConfigMetricData metric;
  models::MetricsConfig metric_config;
  metric.data_key = id;
  metric.value_unit_sign = unit;
  metric.simbols_after_comma = decimals;
  metric.inverse = inverse;
  return {id, std::move(metric)};
}

struct MetricSnapshotSuccessTest : public Test {
  std::shared_ptr<models::MetricsConfig> metrics_config;
  std::shared_ptr<testing::MetricDefinitionMock> metric_definition;
  MetricSnapshot snapshot;
  types::PlaceIds place_ids{types::PlaceId{1}, types::PlaceId{2},
                            types::PlaceId{55}};
  std::string period{"week"};
  std::unordered_map<std::string, types::MetricValue> data_;
  MetricSnapshotSuccessTest()
      : metrics_config(std::make_shared<models::MetricsConfig>()),
        metric_definition(new testing::MetricDefinitionMock(*metrics_config)),
        snapshot(nullptr, metrics_config, metric_definition,
                 types::PlaceIds{types::PlaceId{1}, types::PlaceId{2},
                                 types::PlaceId{55}},
                 "week") {
    metrics_config->metrics.emplace(
        MakeMetric("common_revenue_lost", "₽", 2, true));
    metrics_config->metrics.emplace(
        MakeMetric("common_revenue_earned", "₽", 2, false));
    metrics_config->periods.emplace(
        std::make_pair("week", models::ConfigPeriodData{{"day"}}));
  }
};

TEST_F(MetricSnapshotSuccessTest, Get_error_metric) {
  ASSERT_THROW(snapshot.Get("qwerty"), snapshot::ErrorGetDataMetrics);
}

TEST_F(MetricSnapshotSuccessTest, Get_metrics_full_flow) {
  models::ConfigMetricData data;
  // должны получить только один раз
  EXPECT_CALL(*metric_definition->common_revenue_lost_mock,
              GetTotalValue(_, _, place_ids))
      .WillOnce(Return(100.));
  EXPECT_CALL(*metric_definition->common_revenue_lost_mock,
              GetPrevTotalValue(_, _, place_ids))
      .WillOnce(Return(45.5));
  EXPECT_CALL(*metric_definition->common_revenue_lost_mock,
              GetData(_, _, place_ids))
      .WillOnce(Return(types::PeriodPoints{
          types::PeriodPoint{34, std::nullopt, ::utils::datetime::Now(),
                             ::utils::datetime::Now(), std::nullopt,
                             std::nullopt},
          types::PeriodPoint{39.2, std::nullopt, ::utils::datetime::Now(),
                             ::utils::datetime::Now(), std::nullopt,
                             std::nullopt},
          types::PeriodPoint{41, std::nullopt, ::utils::datetime::Now(),
                             ::utils::datetime::Now(), std::nullopt,
                             std::nullopt}}));

  auto result = snapshot.Get("common_revenue_lost");

  auto common_revenue_lost =
      types::MetricValue{100, 54.5, 41, "100 ₽", "54.50 ₽", "41 ₽"};
  ASSERT_EQ(result, common_revenue_lost);
  //   следующий запрос уже идет без похода в metric_reader
  ASSERT_EQ(snapshot.Get("common_revenue_lost"), common_revenue_lost);

  EXPECT_CALL(*metric_definition->common_revenue_earned_mock,
              GetTotalValue(_, _, place_ids))
      .WillOnce(Return(154.2));
  EXPECT_CALL(*metric_definition->common_revenue_earned_mock,
              GetPrevTotalValue(_, _, place_ids))
      .WillOnce(Return(54.10));
  EXPECT_CALL(*metric_definition->common_revenue_earned_mock,
              GetData(_, _, place_ids))
      .WillOnce(Return(types::PeriodPoints{types::PeriodPoint{
          56.4, std::nullopt, ::utils::datetime::Now(),
          ::utils::datetime::Now(), std::nullopt, std::nullopt}}));
  auto common_revenue_earned = types::MetricValue{
      154.2, 100.1, 56.4, "154.20 ₽", "100.10 ₽", "56.40 ₽"};

  // а вот запрос следующей метрики уже требует похода в реадер
  ASSERT_EQ(snapshot.Get("common_revenue_earned"), common_revenue_earned);
  // повторный - нет
  ASSERT_EQ(snapshot.Get("common_revenue_earned"), common_revenue_earned);
  // походим туда сюда - чтобы проверить, что все данные на месте
  ASSERT_EQ(snapshot.Get("common_revenue_lost"), common_revenue_lost);
  ASSERT_EQ(snapshot.Get("common_revenue_earned"), common_revenue_earned);
}

struct MetricSnapshotErrorEmptyTest : public Test {
  std::shared_ptr<models::MetricsConfig> metrics_config;
  std::shared_ptr<testing::MetricDefinitionMock> metric_definition;
  MetricSnapshot snapshot;
  std::string period{"week"};
  std::unordered_map<std::string, types::MetricValue> data_;
  MetricSnapshotErrorEmptyTest()
      : metrics_config(std::make_shared<models::MetricsConfig>()),
        metric_definition(new testing::MetricDefinitionMock(*metrics_config)),
        snapshot(nullptr, metrics_config, metric_definition, types::PlaceIds{},
                 "week") {
    metrics_config->metrics.emplace(
        MakeMetric("common_revenue_lost", "₽", 2, true));
    metrics_config->metrics.emplace(
        MakeMetric("common_revenue_earned", "₽", 2, false));
    metrics_config->periods.emplace(
        std::make_pair("week", models::ConfigPeriodData{{"day"}}));
  }
};

TEST_F(MetricSnapshotErrorEmptyTest, Get_error_metric) {
  ASSERT_THROW(snapshot.Get("common_revenue_lost"),
               snapshot::ErrorEmptyPlaceIds);
}

struct MetricSnapshotErrorPeriodTest : public Test {
  std::shared_ptr<models::MetricsConfig> metrics_config;
  std::shared_ptr<testing::MetricDefinitionMock> metric_definition;
  MetricSnapshot snapshot;
  types::PlaceIds place_ids{types::PlaceId{1}, types::PlaceId{2},
                            types::PlaceId{55}};
  std::string period{"weekly"};
  std::unordered_map<std::string, types::MetricValue> data_;
  MetricSnapshotErrorPeriodTest()
      : metrics_config(std::make_shared<models::MetricsConfig>()),
        metric_definition(new testing::MetricDefinitionMock(*metrics_config)),
        snapshot(nullptr, metrics_config, metric_definition,
                 types::PlaceIds{types::PlaceId{1}, types::PlaceId{2},
                                 types::PlaceId{55}},
                 "weekly") {
    metrics_config->metrics.emplace(
        MakeMetric("common_revenue_lost", "₽", 2, true));
    metrics_config->metrics.emplace(
        MakeMetric("common_revenue_earned", "₽", 2, false));
    metrics_config->periods.emplace(
        std::make_pair("week", models::ConfigPeriodData{{"day"}}));
  }
};

TEST_F(MetricSnapshotErrorPeriodTest, Get_error_metric) {
  ASSERT_THROW(snapshot.Get("common_revenue_lost"),
               snapshot::ErrorParsePeriodMetric);
}

}  // namespace eats_report_storage::snapshot
