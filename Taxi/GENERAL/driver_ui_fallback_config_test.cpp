#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/driver_ui_fallback_config.hpp>

TEST(TestDriverUiFallback, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& fallback = config.Get<config::driver_ui::FallbackConfig>();

  ASSERT_EQ(fallback.IsEnabled(true), false);
  ASSERT_EQ(fallback.IsEnabled(false), false);
}
