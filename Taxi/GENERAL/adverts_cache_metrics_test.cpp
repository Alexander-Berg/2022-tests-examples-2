#include <gtest/gtest.h>

#include <eats-adverts-goods/components/adverts_cache_metrics.hpp>
#include <eats-adverts-goods/utils/tests.hpp>

namespace eats_adverts_goods::components::stats {

namespace {

formats::json::ValueBuilder MakeSolomonLabel(const std::string& label) {
  formats::json::ValueBuilder meta_builder(formats::common::Type::kObject);
  meta_builder["solomon_children_labels"] = label;
  formats::json::ValueBuilder label_builder(formats::common::Type::kObject);
  label_builder["$meta"] = meta_builder;
  return label_builder;
}

formats::json::ValueBuilder MakeEmptyDump() {
  auto builder = MakeSolomonLabel("promo-type");
  builder["restaurants"] = MakeSolomonLabel("promo-name");
  builder["retail"] = MakeSolomonLabel("promo-name");
  return builder;
}

formats::json::ValueBuilder MakeTableStatsDump(size_t items_count,
                                               size_t places_count,
                                               size_t errors_count) {
  formats::json::ValueBuilder builder(formats::common::Type::kObject);
  builder["items_count"] = items_count;
  builder["places_count"] = places_count;
  builder["parsing_errors_count"] = errors_count;
  return builder;
}

void AssertDumpsEq(const formats::json::Value& expected,
                   const formats::json::Value& actual) {
  ASSERT_EQ(expected, actual) << "expected: " << ToString(expected) << ";\n"
                              << "actual:   " << ToString(actual) << ".";
}

}  // namespace

TEST(TestAdvertsCacheMetrics, TestDump) {
  AdvertsCacheMetrics metrics_storage{};

  // dump is empty
  AssertDumpsEq(MakeEmptyDump().ExtractValue(), metrics_storage.DumpMetrics());

  // fill with empty data
  metrics_storage.SetMetrics({});
  AssertDumpsEq(MakeEmptyDump().ExtractValue(), metrics_storage.DumpMetrics());

  // fill with non-empty data
  stats::AdvertsCacheMetrics::MetricsStorage data{};
  data[models::Promotion{"test_promo"}] = CachedTableStats{
      models::TableType::kRestaurants,  // table_type
      100,                              // items_count
      10,                               // places_count
      0,                                // parsing_error_count
  };
  data[models::Promotion{"test_promo_2"}] = CachedTableStats{
      models::TableType::kRetail,  // table_type
      20,                          // items_count
      1,                           // places_count
      100,                         // parsing_error_count
  };
  metrics_storage.SetMetrics(std::move(data));

  auto expected_value_builder = MakeEmptyDump();
  expected_value_builder["restaurants"]["test_promo"] =
      MakeTableStatsDump(100, 10, 0);
  expected_value_builder["retail"]["test_promo_2"] =
      MakeTableStatsDump(20, 1, 100);

  AssertDumpsEq(expected_value_builder.ExtractValue(),
                metrics_storage.DumpMetrics());

  // append more data
  stats::AdvertsCacheMetrics::MetricsStorage incremental_data{};
  incremental_data[models::Promotion{"test_promo"}] = CachedTableStats{
      models::TableType::kRestaurants,  // table_type
      10,                               // items_count
      1,                                // places_count
      10,                               // parsing_error_count
  };
  metrics_storage.AppendMetrics(std::move(incremental_data));
  auto expected_value_builder_incremental = MakeEmptyDump();
  expected_value_builder_incremental["restaurants"]["test_promo"] =
      MakeTableStatsDump(110, 11, 10);
  expected_value_builder_incremental["retail"]["test_promo_2"] =
      MakeTableStatsDump(20, 1, 100);

  AssertDumpsEq(expected_value_builder_incremental.ExtractValue(),
                metrics_storage.DumpMetrics());
}

}  // namespace eats_adverts_goods::components::stats
