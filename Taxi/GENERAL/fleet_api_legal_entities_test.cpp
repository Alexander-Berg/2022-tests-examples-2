#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/fleet_api_legal_entities.hpp>

TEST(TestLegalEntitiesConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& test_config = config.Get<config::FleetApiLegalEntities>();
  ASSERT_EQ(1000u, *test_config.rph);
}
