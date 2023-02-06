#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/pickup_points_config.hpp>

TEST(BlockedZonesEnabledConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& blocked_zones_enabled =
      config.Get<config::PickupPointsProtocolConfig>().blocked_zones_enabled;
  ASSERT_EQ(blocked_zones_enabled, true);
}
