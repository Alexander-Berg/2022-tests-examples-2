#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/activity_history_using_no_dm_proxy_config.hpp>
#include <config/config.hpp>

TEST(TestActivityHistoryUsingNoDMProxyConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& activity_history_using_no_dm_proxy_config =
      config.Get<config::ActivityHistoryUsingNoDMProxy>();
  ASSERT_EQ(activity_history_using_no_dm_proxy_config
                .activity_history_using_no_dm_proxy,
            0u);
}
