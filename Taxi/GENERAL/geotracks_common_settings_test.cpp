#include "geotracks_common_settings.hpp"

#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>

TEST(GeotracksCommonSettingsConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& gt_config = config.Get<config::GeotracksCommonSettings>();
  ASSERT_EQ(false, gt_config.api_keys_enable());
}
