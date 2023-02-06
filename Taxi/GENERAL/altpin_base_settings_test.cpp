#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/altpin_base_settings.hpp>
#include <config/config.hpp>

TEST(TestAltpinBaseSettings, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& altpin_base_settings = config.Get<config::AltpinBaseSettings>();
  ASSERT_EQ(180, altpin_base_settings.min_eta_gain);
}
