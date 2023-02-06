#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/yt_settings.hpp>

TEST(TestYtSettings, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& yt_settings = config.Get<config::YtSettings>();
  ASSERT_FALSE(yt_settings.hosts_update_enabled);
}
