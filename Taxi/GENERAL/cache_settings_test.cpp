#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/cache_settings.hpp>
#include <config/config.hpp>

TEST(TestCacheSettings, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& test_config = config.Get<config::CacheSettingsConfig>();

  ASSERT_TRUE(test_config.config["SomeCache"].is_dump_enabled);
  ASSERT_FALSE(test_config.config["SomeCache"].is_partial_update_enabled);
  ASSERT_EQ(test_config.config["SomeCache"].partial_update_sleep_sec,
            std::chrono::seconds(60u));
  ASSERT_EQ(test_config.config["SomeCache"].num_docks_per_update, 1000000u);
}
