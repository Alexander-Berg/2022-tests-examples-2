#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/suggest_settings.hpp>

TEST(TestSuggestSettings, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& suggest_settings = config.Get<config::SuggestSettings>();
  ASSERT_EQ("http://suggest-maps.yandex.net/suggest-geo",
            suggest_settings.geo_api_host);
}
