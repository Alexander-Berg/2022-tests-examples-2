#include <gtest/gtest.h>

#include <modules/zoneinfo-core/core/tariff_requirements/filters.hpp>
#include <testing/taxi_config.hpp>

#include "../test_utils/mock_experiments.hpp"

namespace zoneinfo::core {

namespace {

Experiments3 MockExperiments3Local() {
  formats::json::ValueBuilder disabled_requirement_builder;
  formats::json::ValueBuilder cat_array_builder(formats::json::Type::kArray);
  cat_array_builder.PushBack("econom");
  disabled_requirement_builder["req_skip_by_exp"] =
      cat_array_builder.ExtractValue();

  auto disabled_requirement_value = disabled_requirement_builder.ExtractValue();
  return MockExperiments3(
      {{"disabled_requirement_req_skip_by_exp", disabled_requirement_value}});
}

taxi_config::TaxiConfig MockConfig() {
  auto taxi_config =
      dynamic_config::GetDefaultSnapshot().Get<taxi_config::TaxiConfig>();

  taxi_config.fake_requirements_config = {{"req_skip_by_fake"}};

  return taxi_config;
}

}  // namespace

TEST(TestRequirementsFilters, All) {
  auto taxi_config = MockConfig();
  auto experiments3 = MockExperiments3Local();
  ASSERT_EQ(
      ShouldBeSkipped("req_skip_by_fake", "econom", taxi_config, experiments3),
      true);
  ASSERT_EQ(
      ShouldBeSkipped("req_skip_by_exp", "econom", taxi_config, experiments3),
      true);
  ASSERT_EQ(
      ShouldBeSkipped("req_skip_by_exp", "comfort", taxi_config, experiments3),
      false);
  ASSERT_EQ(ShouldBeSkipped("req_ok", "econom", taxi_config, experiments3),
            false);
}

}  // namespace zoneinfo::core
