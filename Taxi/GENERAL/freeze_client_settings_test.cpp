#include "freeze_client_settings.hpp"

#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>

TEST(DriverFreezeClientConfigs, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& client_config = config.Get<config::DriverFreeze>();
  ASSERT_EQ(300, client_config.timeout_ms().count());
  ASSERT_EQ(3u, client_config.retries());
  ASSERT_EQ(2000, client_config.frozen_timeout_ms().count());
  ASSERT_EQ(3u, client_config.frozen_retries());
}
