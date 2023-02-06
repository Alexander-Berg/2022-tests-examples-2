#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>

#include "dispatch_airport_cache_config.hpp"

TEST(TestDispatchAirportConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& cfg = config.Get<config::DispatchAirportCacheConfig>();

  const auto& request_settings = cfg.request_settings;
  const auto it = request_settings.Get("any_api");
  ASSERT_EQ(3, it->attempts);
  ASSERT_EQ(std::chrono::milliseconds(200), it->timeout_ms);

  ASSERT_EQ(false, cfg.update_airport_queues_cache_enabled);
}
