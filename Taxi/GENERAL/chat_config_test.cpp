#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/chat_config.hpp>
#include <config/config.hpp>

TEST(TestChatConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::ChatConfig& chat_config = config.Get<config::ChatConfig>();
  ASSERT_EQ(chat_config.translation_enabled, false);
  ASSERT_EQ(chat_config.translations_yt_log_enabled, false);
  ASSERT_EQ(chat_config.translation_max_groups, static_cast<size_t>(6));
}
