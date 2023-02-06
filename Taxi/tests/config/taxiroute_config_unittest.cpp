#include "config/taxiroute_config.hpp"

#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>

TEST(TestTaxirouteConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& shade_car_config = config.Get<config::TaxiRouteConfig>();

  ASSERT_EQ(shade_car_config.shade_car_on.Get(), false);
  ASSERT_EQ(shade_car_config.shade_car_max_radius.Get(), 500);
  ASSERT_EQ(shade_car_config.shade_car_accuracy_radius.Get(), 30);
}
