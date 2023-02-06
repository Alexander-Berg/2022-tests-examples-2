#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/uber_suggest_settings.hpp>

TEST(TestUberSuggestSettings, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& uber_suggest_settings = config.Get<config::UberSuggestSettings>();
  ASSERT_EQ(40075000.0, uber_suggest_settings.too_far_threshold);
}
