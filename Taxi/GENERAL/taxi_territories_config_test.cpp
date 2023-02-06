#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/taxi_territories_config.hpp>

TEST(TestTaxiTerritories, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::TaxiTerritories& taxi_territories_config =
      config.Get<config::TaxiTerritories>();

  ASSERT_EQ(taxi_territories_config.taxi_territories_timeout_ms.Get(), 250);
  ASSERT_EQ(taxi_territories_config.taxi_territories_retries.Get(), 3);
}
