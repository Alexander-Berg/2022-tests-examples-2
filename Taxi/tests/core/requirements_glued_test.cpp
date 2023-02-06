#include <gtest/gtest.h>

#include <modules/zoneinfo-core/core/tariff_requirements/glued.hpp>

#include "../test_utils/mock_experiments.hpp"

namespace zoneinfo::core {

namespace {

Experiments3 MockExperiments3Toggle() {
  formats::json::ValueBuilder toggle_to_glued_builder;
  formats::json::ValueBuilder cat_array_builder(formats::json::Type::kArray);
  cat_array_builder.PushBack("cargo");
  toggle_to_glued_builder["tariffs"] = cat_array_builder.ExtractValue();

  auto toggle_to_glued_value = toggle_to_glued_builder.ExtractValue();
  return MockExperiments3({{"toggle_to_glued", toggle_to_glued_value}});
}

clients::taxi_tariffs::Category MockCategory() {
  clients::taxi_tariffs::Category cargo;
  cargo.name = "cargo";
  cargo.glued_requirements = {"glued_req"};
  return cargo;
}

}  // namespace

TEST(TestRequirementsGlued, All) {
  auto ts_category = MockCategory();
  auto experiments3 = MockExperiments3({});
  ASSERT_EQ(GetGluedInfo("glued_req", ts_category, experiments3).glued, true);
  ASSERT_EQ(GetGluedInfo("toggled_glued_req", ts_category, experiments3).glued,
            false);
}

TEST(TestRequirementsGlued, Toggle) {
  auto ts_category = MockCategory();
  auto experiments3 = MockExperiments3Toggle();
  ASSERT_EQ(GetGluedInfo("glued_req", ts_category, experiments3).glued, true);
  ASSERT_EQ(GetGluedInfo("toggled_glued_req", ts_category, experiments3).glued,
            true);
}

}  // namespace zoneinfo::core
