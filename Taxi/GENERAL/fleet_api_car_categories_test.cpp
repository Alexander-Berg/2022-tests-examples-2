#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/fleet_api_car_categories.hpp>

TEST(TestServicesGarCategories, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& test_config = config.Get<config::FleetApiCarCategories>();

  ASSERT_TRUE(test_config.external_categories.empty());
  ASSERT_TRUE(test_config.internal_categories.empty());
}
