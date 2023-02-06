#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/maps_static_api.hpp>

TEST(TestMapsStaticApi, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& maps_static_api = config.Get<config::MapsStaticApi>();
  ASSERT_EQ(maps_static_api.url_with_key,
            "https://tc.mobile.yandex.net/get-map/1.x/?");
}
