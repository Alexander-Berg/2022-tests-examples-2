#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/taximeter_version_settings.hpp>

TEST(TestTaximeterVersionSettings, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& taximeter_version_settings =
      config.Get<config::TaximeterVersionSettings>();

  ASSERT_EQ("8.30", taximeter_version_settings.current.ToString());
}
