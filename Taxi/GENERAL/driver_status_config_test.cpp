#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>

#include "driver_status_config.hpp"

TEST(TestDriverStatusConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& driver_status_config = config.Get<config::DriverStatus>();

  ASSERT_EQ(driver_status_config.max_age_hours_in_cache.Get(),
            std::chrono::hours(4));
  ASSERT_EQ(driver_status_config.caches_settings.GetMap().size(), 1u);
  ASSERT_EQ(driver_status_config.caches_settings.GetDefault().cache_enabled,
            true);
  ASSERT_EQ(driver_status_config.caches_settings.GetDefault()
                .full_update_request_parts_count,
            2);
}
