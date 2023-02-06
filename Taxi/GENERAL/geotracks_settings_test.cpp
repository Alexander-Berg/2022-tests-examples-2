#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/geotracks_settings.hpp>

TEST(TestGeotracksSettings, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::GeotracksSettings& geotracks_settings =
      config.Get<config::GeotracksSettings>();
  ASSERT_EQ(geotracks_settings.reader.use_ls_limit, 3u);
}
