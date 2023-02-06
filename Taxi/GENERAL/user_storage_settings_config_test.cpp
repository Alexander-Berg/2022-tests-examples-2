#include "user_storage_settings_config.hpp"

#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>

TEST(UserStorageSettingsConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& ut_config = config.Get<config::UserStorageSettings>();
  ASSERT_EQ(std::chrono::hours(3), ut_config.points_ttl());
  ASSERT_EQ(ut_config.history_enable, false);
}
