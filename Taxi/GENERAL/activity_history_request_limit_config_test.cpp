#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/activity_history_request_limit_config.hpp>
#include <config/config.hpp>

TEST(TestActivityHistoryRequestLimitConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& activity_history_limit_config =
      config.Get<config::ActivityHistoryRequestLimit>();
  ASSERT_EQ(activity_history_limit_config.activity_history_request_limit, 0u);
}
