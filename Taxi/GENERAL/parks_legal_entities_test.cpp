#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/parks_legal_entities.hpp>

TEST(TestLegalEntitiesConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& test_config = config.Get<config::ParksLegalEntities>();
  EXPECT_TRUE(test_config.enable_dadata_validation);
  EXPECT_FALSE(test_config.allow_dadata_invalid_result);
  EXPECT_TRUE(test_config.use_park_default_work_hours);
  EXPECT_TRUE(test_config.check_private_address);
  EXPECT_EQ(0u, test_config.stop_list->size());
  EXPECT_EQ(0u, test_config.supported_countries->size());
}
