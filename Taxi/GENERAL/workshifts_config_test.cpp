#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/workshifts_config.hpp>

TEST(TestWorkshiftsConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& workshifts_config = config.Get<config::Workshifts>();
  ASSERT_EQ(workshifts_config.tags_enabled, false);
  ASSERT_EQ(workshifts_config.cache_update_enabled, false);
  ASSERT_EQ(workshifts_config.check_workshifts_enabled, false);
}
