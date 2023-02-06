#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include "client_geo_config.hpp"

TEST(TestClientGeo, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::ClientGeo& client_geo_config = config.Get<config::ClientGeo>();

  ASSERT_EQ(client_geo_config.track_in_background.Get(), false);
  ASSERT_EQ(client_geo_config.false_count.Get(), 10);
  ASSERT_EQ(client_geo_config.tracking_rate_battery_state_full.Get(), 10);
  ASSERT_EQ(client_geo_config.tracking_rate_battery_state_half.Get(), 20);
  ASSERT_EQ(client_geo_config.tracking_rate_battery_state_empty.Get(), 30);
  ASSERT_EQ(client_geo_config.request_max_requests.Get(), 3);
  ASSERT_EQ(client_geo_config.request_version.Get(), "v1.0");
  ASSERT_EQ(client_geo_config.disable_distance.Get(), 900);
}
