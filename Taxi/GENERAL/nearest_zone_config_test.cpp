#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/nearest_zone_config.hpp>

TEST(TestNearestZoneConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::NearestZoneConfig& nearest_zone_config =
      config.Get<config::NearestZoneConfig>();

  ASSERT_EQ(nearest_zone_config.not_ua_zones.Get().size(), 8u);

  const boost::optional<config::ComingSoonZoneSettings> settings =
      nearest_zone_config.zones_coming_soon.Get("tel_aviv_activation");
  ASSERT_TRUE(settings.is_initialized());
  ASSERT_FALSE(settings->message.empty());
  ASSERT_TRUE(settings->urls.size() == 1u);
  ASSERT_FALSE(settings->url_text.empty());

  ASSERT_EQ(nearest_zone_config.show_message_404, false);
}
