#include <userver/utest/utest.hpp>

#include <testing/source_path.hpp>

#include <components/metrics/common/metrics_descriptor.hpp>

namespace {
formats::json::Value LoadJson(const std::string& fname) {
  static const std::string path(utils::CurrentSourcePath("src/tests/static/"));
  return formats::json::blocking::FromFile(path + fname);
}
}  // namespace

namespace components::metrics::test {

TEST(TestValueBuilderAt, FullPath) {
  common::MetricsDescriptor descriptor{"zone", "tariff",
                                       models::SupplyState::kPaidSupplyEnabled};
  formats::json::ValueBuilder builder(formats::json::Type::kObject);
  auto full_path_result =
      common::ValueBuilderAt(builder, descriptor, "metric_name");
  full_path_result = 15;
  auto expected_json = LoadJson("full_path.json");
  ASSERT_EQ(builder.ExtractValue(), expected_json);
}

TEST(TestValueBuilderAt, PathWithoutZoneField) {
  common::MetricsDescriptor descriptor{std::nullopt, "tariff",
                                       models::SupplyState::kPaidSupplyEnabled};
  formats::json::ValueBuilder builder(formats::json::Type::kObject);
  auto result = common::ValueBuilderAt(builder, descriptor, "metric_name");
  result = 15;
  auto expected_json = LoadJson("path_without_zone_field.json");
  ASSERT_EQ(builder.ExtractValue(), expected_json);
}

TEST(TestValueBuilderAt, PathWithoutTariffField) {
  common::MetricsDescriptor descriptor{
      "zone", std::nullopt, models::SupplyState::kNoCarsOrderEnabled};
  formats::json::ValueBuilder builder(formats::json::Type::kObject);
  auto result = common::ValueBuilderAt(builder, descriptor, "metric_name");
  result = 15;
  auto expected_json = LoadJson("path_without_tariff_field.json");
  ASSERT_EQ(builder.ExtractValue(), expected_json);
}

TEST(TestValueBuilderAt, PathWithoutSupplyStateField) {
  common::MetricsDescriptor descriptor{"zone", "tariff", std::nullopt};
  formats::json::ValueBuilder builder(formats::json::Type::kObject);
  auto result = common::ValueBuilderAt(builder, descriptor, "metric_name");
  result = 15;
  auto expected_json = LoadJson("path_without_supply_state_field.json");
  ASSERT_EQ(builder.ExtractValue(), expected_json);
}

TEST(TestValueBuilderAt, PathWithSingleField) {
  common::MetricsDescriptor descriptor{std::nullopt, std::nullopt,
                                       std::nullopt};
  formats::json::ValueBuilder builder(formats::json::Type::kObject);
  auto result = common::ValueBuilderAt(builder, descriptor, "metric_name");
  result = 15;
  auto expected_json = LoadJson("path_with_single_field.json");
  ASSERT_EQ(builder.ExtractValue(), expected_json);
}

}  // namespace components::metrics::test
