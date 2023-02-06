#include <clients/eats-place-rating/client_gmock.hpp>
#include <components/benchmarks.hpp>
#include <userver/utest/utest.hpp>
#include "metric_reader_mocks.hpp"

namespace eats_report_storage::types {
inline bool operator==(const Benchmark& lhs, const Benchmark& rhs) {
  return std::make_tuple(lhs.metric, lhs.value, lhs.reference, lhs.is_bad) ==
         std::make_tuple(rhs.metric, rhs.value, rhs.reference, rhs.is_bad);
}
}  // namespace eats_report_storage::types

namespace eats_report_storage::components::impl {
using namespace ::testing;

struct BenchmarkComponentTest : public Test {
  StrictMock<clients::eats_place_rating::ClientGMock> eats_place_rating;

  Benchmarks benchmarks;

  types::PlaceIds place_ids;
  ConfigBenchmarks benchmarks_config;
  models::MetricsConfig metrics_config;

  static std::pair<std::string, ConfigBenchmark> MakeBenchmark(
      const std::string& slug, const std::string& metric,
      std::optional<double> reference) {
    ConfigBenchmark benchmark;
    benchmark.title = slug;
    benchmark.benchmark_slug = slug;
    benchmark.metric_slug = metric;
    benchmark.reference_fallback = reference;
    benchmark.period =
        taxi_config::eats_report_storage_benchmarks::BenchmarkPeriod::kWeek;
    return {slug, std::move(benchmark)};
  }

  static std::pair<std::string, models::ConfigMetricData> MakeMetric(
      const std::string& id, const std::optional<std::string>& unit,
      int decimals, bool inverse,
      std::optional<double> reference_value = std::nullopt) {
    models::ConfigMetricData metric;
    metric.data_key = id;
    metric.value_unit_sign = unit;
    metric.simbols_after_comma = decimals;
    metric.inverse = inverse;
    if (reference_value) {
      metric.reference_value = models::ReferenceValue{*reference_value, "", ""};
    }
    return {id, std::move(metric)};
  }

  BenchmarkComponentTest() : benchmarks(nullptr, eats_place_rating) {
    place_ids.emplace_back(10);

    benchmarks_config.emplace(
        MakeBenchmark("average_rating", "rating_average", 4.3));
    benchmarks_config.emplace(
        MakeBenchmark("cancel_rating", "rating_cancel", std::nullopt));
    benchmarks_config.emplace(
        MakeBenchmark("revenue_lost", "common_revenue_lost", 1000.001));
    benchmarks_config.emplace(
        MakeBenchmark("order_count", "common_order_count", 200));
    benchmarks_config.emplace(
        MakeBenchmark("revenue_earned", "common_revenue_earned", 1000.001));
    benchmarks_config.emplace(
        MakeBenchmark("not_in_config", "not_in_config", 0.0));
    benchmarks_config.emplace(
        MakeBenchmark("unknown_metric", "unknown_metric", 0.0));
    benchmarks_config.emplace(
        MakeBenchmark("no_reader_metric", "common_order_success_count", 0.0));

    metrics_config.metrics.emplace(
        MakeMetric("rating_average", std::nullopt, 1, false));
    metrics_config.metrics.emplace(
        MakeMetric("rating_cancel", std::nullopt, 1, false));

    metrics_config.metrics.emplace(
        MakeMetric("common_order_count", std::nullopt, 1, false, 350));

    metrics_config.metrics.emplace(
        MakeMetric("common_revenue_lost", "₽", 2, true));
    metrics_config.metrics.emplace(
        MakeMetric("common_revenue_earned", "₽", 2, false));
    metrics_config.metrics.emplace(
        MakeMetric("unknown_metric", std::nullopt, 1, false));
    metrics_config.metrics.emplace(
        MakeMetric("common_order_success_count", std::nullopt, 0, false));
    metrics_config.metrics.emplace(
        MakeMetric("not_in_benchmarks", std::nullopt, 0, false));

    metrics_config.periods.emplace(
        std::make_pair("week", models::ConfigPeriodData{{"day"}}));
  }
};

TEST_F(BenchmarkComponentTest,
       GetBenchmarks_skips_benchmark_not_in_bemchmarks_config) {
  testing::MetricDefinitionMock metric_definition{metrics_config};
  const auto result = benchmarks.GetBenchmarks(
      benchmarks_config, metrics_config, metric_definition, place_ids,
      {types::BenchmarkSlug{"not_in_benchmarks"}});
  ASSERT_TRUE(result.empty());
}

TEST_F(BenchmarkComponentTest,
       GetBenchmarks_skips_benchmark_without_reference) {
  testing::MetricDefinitionMock metric_definition{metrics_config};
  const auto result = benchmarks.GetBenchmarks(
      benchmarks_config, metrics_config, metric_definition, place_ids,
      {types::BenchmarkSlug{"cancel_rating"}});
  ASSERT_TRUE(result.empty());
}

TEST_F(BenchmarkComponentTest,
       GetBenchmarks_skips_benchmark_with_metric_not_in_config) {
  testing::MetricDefinitionMock metric_definition{metrics_config};
  const auto result = benchmarks.GetBenchmarks(
      benchmarks_config, metrics_config, metric_definition, place_ids,
      {types::BenchmarkSlug{"not_in_config"}});
  ASSERT_TRUE(result.empty());
}

TEST_F(BenchmarkComponentTest,
       GetBenchmarks_skips_benchmark_with_unknown_metric) {
  testing::MetricDefinitionMock metric_definition{metrics_config};
  const auto result = benchmarks.GetBenchmarks(
      benchmarks_config, metrics_config, metric_definition, place_ids,
      {types::BenchmarkSlug{"unknown_metric"}});
  ASSERT_TRUE(result.empty());
}

TEST_F(BenchmarkComponentTest,
       GetBenchmarks_skips_benchmark_with_metric_wthout_reader) {
  testing::MetricDefinitionMock metric_definition{metrics_config};
  const auto result = benchmarks.GetBenchmarks(
      benchmarks_config, metrics_config, metric_definition, place_ids,
      {types::BenchmarkSlug{"no_reader_metric"}});
  ASSERT_TRUE(result.empty());
}

TEST_F(BenchmarkComponentTest,
       GetBenchmarks_skips_benchmark_with_metric_wthout_total) {
  eats_report_storage::testing::MetricDefinitionMock metric_definition{
      metrics_config};
  EXPECT_CALL(*metric_definition.common_revenue_lost_mock,
              GetTotalValue(_, _, place_ids))
      .WillOnce(Return(std::nullopt));
  const auto result = benchmarks.GetBenchmarks(
      benchmarks_config, metrics_config, metric_definition, place_ids,
      {types::BenchmarkSlug{"revenue_lost"}});
  ASSERT_TRUE(result.empty());
}

TEST_F(BenchmarkComponentTest,
       GetBenchmarks_return_benchmark_for_metric_with_good_value) {
  eats_report_storage::testing::MetricDefinitionMock metric_definition{
      metrics_config};
  EXPECT_CALL(*metric_definition.common_revenue_earned_mock,
              GetTotalValue(_, _, place_ids))
      .WillOnce(Return(1000.123));
  const auto result = benchmarks.GetBenchmarks(
      benchmarks_config, metrics_config, metric_definition, place_ids,
      {types::BenchmarkSlug{"revenue_earned"}});
  ASSERT_THAT(result,
              ElementsAre(types::Benchmark{
                  "revenue_earned", {}, "1 000.12 ₽", "1 000 ₽", false}));
}

TEST_F(BenchmarkComponentTest,
       GetBenchmarks_return_benchmark_for_metric_with_bad_value) {
  eats_report_storage::testing::MetricDefinitionMock metric_definition{
      metrics_config};
  EXPECT_CALL(*metric_definition.common_revenue_earned_mock,
              GetTotalValue(_, _, place_ids))
      .WillOnce(Return(999.937));
  const auto result = benchmarks.GetBenchmarks(
      benchmarks_config, metrics_config, metric_definition, place_ids,
      {types::BenchmarkSlug{"revenue_earned"}});
  ASSERT_THAT(result,
              ElementsAre(types::Benchmark{
                  "revenue_earned", {}, "999.94 ₽", "1 000 ₽", true}));
}

TEST_F(BenchmarkComponentTest,
       GetBenchmarks_return_benchmark_for_inverse_metric_with_bad_value) {
  eats_report_storage::testing::MetricDefinitionMock metric_definition{
      metrics_config};
  EXPECT_CALL(*metric_definition.common_revenue_lost_mock,
              GetTotalValue(_, _, place_ids))
      .WillOnce(Return(1000.123));
  const auto result = benchmarks.GetBenchmarks(
      benchmarks_config, metrics_config, metric_definition, place_ids,
      {types::BenchmarkSlug{"revenue_lost"}});
  ASSERT_THAT(result,
              ElementsAre(types::Benchmark{
                  "revenue_lost", {}, "1 000.12 ₽", "1 000 ₽", true}));
}

TEST_F(BenchmarkComponentTest,
       GetBenchmarks_return_benchmark_for_inverse_metric_with_good_value) {
  eats_report_storage::testing::MetricDefinitionMock metric_definition{
      metrics_config};
  EXPECT_CALL(*metric_definition.common_revenue_lost_mock,
              GetTotalValue(_, _, place_ids))
      .WillOnce(Return(999.937));
  const auto result = benchmarks.GetBenchmarks(
      benchmarks_config, metrics_config, metric_definition, place_ids,
      {types::BenchmarkSlug{"revenue_lost"}});
  ASSERT_THAT(result,
              ElementsAre(types::Benchmark{
                  "revenue_lost", {}, "999.94 ₽", "1 000 ₽", false}));
}

TEST_F(BenchmarkComponentTest,
       GetBenchmarks_skips_benchmark_with_rating_metric_on_empty_rating) {
  testing::MetricDefinitionMock metric_definition{metrics_config};
  clients::eats_place_rating::eats_v1_eats_place_rating_v1_places_rating_info::
      get::Response response;
  EXPECT_CALL(eats_place_rating, EatsV1EatsPlaceRatingV1PlacesRatingInfo(_, _))
      .WillOnce(Return(response));
  const auto result = benchmarks.GetBenchmarks(
      benchmarks_config, metrics_config, metric_definition, place_ids,
      {types::BenchmarkSlug{"average_rating"}});
  ASSERT_TRUE(result.empty());
}

TEST_F(BenchmarkComponentTest,
       GetBenchmarks_skips_benchmark_with_rating_metric_on_hidden_rating) {
  testing::MetricDefinitionMock metric_definition{metrics_config};
  clients::eats_place_rating::eats_v1_eats_place_rating_v1_places_rating_info::
      get::Response response;
  clients::eats_place_rating::PlaceRatingInfo info;
  info.place_id = 10;
  info.average_rating = 4.6;
  info.show_rating = false;
  response.places_rating_info.emplace_back(std::move(info));
  EXPECT_CALL(eats_place_rating, EatsV1EatsPlaceRatingV1PlacesRatingInfo(_, _))
      .WillOnce(Return(response));
  const auto result = benchmarks.GetBenchmarks(
      benchmarks_config, metrics_config, metric_definition, place_ids,
      {types::BenchmarkSlug{"average_rating"}});
  ASSERT_TRUE(result.empty());
}

TEST_F(BenchmarkComponentTest,
       GetBenchmarks_return_benchmark_for_rating_metric_with_bad_value) {
  testing::MetricDefinitionMock metric_definition{metrics_config};

  clients::eats_place_rating::eats_v1_eats_place_rating_v1_places_rating_info::
      get::Response response;
  clients::eats_place_rating::PlaceRatingInfo info;
  info.place_id = 10;
  info.average_rating = 4.19;
  info.show_rating = true;
  response.places_rating_info.emplace_back(std::move(info));
  EXPECT_CALL(eats_place_rating, EatsV1EatsPlaceRatingV1PlacesRatingInfo(_, _))
      .WillOnce(Return(response));
  const auto result = benchmarks.GetBenchmarks(
      benchmarks_config, metrics_config, metric_definition, place_ids,
      {types::BenchmarkSlug{"average_rating"}});
  ASSERT_THAT(result, ElementsAre(types::Benchmark{
                          "average_rating", {}, "4.2", "4.3", true}));
}

TEST_F(BenchmarkComponentTest,
       GetBenchmarks_return_benchmark_for_rating_metric_with_good_value) {
  testing::MetricDefinitionMock metric_definition{metrics_config};

  clients::eats_place_rating::eats_v1_eats_place_rating_v1_places_rating_info::
      get::Response response;
  clients::eats_place_rating::PlaceRatingInfo info;
  info.place_id = 10;
  info.average_rating = 4.31;
  info.show_rating = true;
  response.places_rating_info.emplace_back(std::move(info));
  EXPECT_CALL(eats_place_rating, EatsV1EatsPlaceRatingV1PlacesRatingInfo(_, _))
      .WillOnce(Return(response));
  const auto result = benchmarks.GetBenchmarks(
      benchmarks_config, metrics_config, metric_definition, place_ids,
      {types::BenchmarkSlug{"average_rating"}});
  ASSERT_THAT(result, ElementsAre(types::Benchmark{
                          "average_rating", {}, "4.3", "4.3", false}));
}

TEST_F(BenchmarkComponentTest, GetBenchmarks_return_multiple_benchmarks) {
  testing::MetricDefinitionMock metric_definition_{metrics_config};
  {
    InSequence seq;
    EXPECT_CALL(*metric_definition_.common_revenue_earned_mock,
                GetTotalValue(_, _, place_ids))
        .WillOnce(Return(1000.123));
    clients::eats_place_rating::
        eats_v1_eats_place_rating_v1_places_rating_info::get::Response response;
    clients::eats_place_rating::PlaceRatingInfo info;
    info.place_id = 10;
    info.average_rating = 4.19;
    info.show_rating = true;
    response.places_rating_info.emplace_back(std::move(info));
    EXPECT_CALL(eats_place_rating,
                EatsV1EatsPlaceRatingV1PlacesRatingInfo(_, _))
        .WillOnce(Return(response));
  }
  const auto result = benchmarks.GetBenchmarks(
      benchmarks_config, metrics_config, metric_definition_, place_ids,
      {types::BenchmarkSlug{"revenue_earned"},
       types::BenchmarkSlug{"average_rating"}});
  ASSERT_THAT(
      result,
      ElementsAre(
          types::Benchmark{
              "revenue_earned", {}, "1 000.12 ₽", "1 000 ₽", false},
          types::Benchmark{"average_rating", {}, "4.2", "4.3", true}));
}

TEST_F(BenchmarkComponentTest,
       GetBenchmarks_return_with_referece_value_metric) {
  eats_report_storage::testing::MetricDefinitionMock metric_definition{
      metrics_config};
  EXPECT_CALL(*metric_definition.common_order_count_mock,
              GetTotalValue(_, _, place_ids))
      .WillOnce(Return(250));
  const auto result = benchmarks.GetBenchmarks(
      benchmarks_config, metrics_config, metric_definition, place_ids,
      {types::BenchmarkSlug{"order_count"}});
  // is_bad = true, потому что установлен референс на метрике 350
  ASSERT_THAT(result, ElementsAre(types::Benchmark{
                          "order_count", {}, "250", "350", true}));
}

TEST_F(BenchmarkComponentTest,
       GetBenchmarks_return_with_referece_false_value_metric) {
  eats_report_storage::testing::MetricDefinitionMock metric_definition{
      metrics_config};
  EXPECT_CALL(*metric_definition.common_order_count_mock,
              GetTotalValue(_, _, place_ids))
      .WillOnce(Return(450));
  const auto result = benchmarks.GetBenchmarks(
      benchmarks_config, metrics_config, metric_definition, place_ids,
      {types::BenchmarkSlug{"order_count"}});
  // is_bad = false, потому что установлен референс на метрике 350
  ASSERT_THAT(result, ElementsAre(types::Benchmark{
                          "order_count", {}, "450", "350", false}));
}

}  // namespace eats_report_storage::components::impl
