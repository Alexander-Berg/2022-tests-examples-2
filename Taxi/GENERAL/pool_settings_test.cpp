#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/pool_settings.hpp>

TEST(TestPoolSettings, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& pool_settings = config.Get<config::PoolSettings>();
  ASSERT_EQ(600u, pool_settings.max_absolute_trip_extending);
}
