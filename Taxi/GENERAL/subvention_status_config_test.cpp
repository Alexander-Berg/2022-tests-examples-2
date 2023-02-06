#include "subvention_status_config.hpp"

#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>

TEST(TestSubventionStatusConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::SubventionStatusConfig& subvention_groups_config =
      config.Get<config::SubventionStatusConfig>();

  ASSERT_EQ(
      subvention_groups_config.geo_booking_show_zero_activity_restrictions,
      true);
  ASSERT_EQ(subvention_groups_config.geo_booking_show_payment_restrictions,
            false);
  ASSERT_EQ(subvention_groups_config.subvention_view_status_proxy_mode,
            models::subvention_view::ProxyMode::kNoProxy);
}
