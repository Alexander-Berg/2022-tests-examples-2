#include "user_archiver_settings.hpp"

#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>

TEST(UserArchiverSettingsConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& gt_config = config.Get<config::UserArchiverSettings>();
  ASSERT_EQ(std::chrono::minutes(10), gt_config.master_period_min());
  ASSERT_EQ(std::chrono::seconds(60), gt_config.master_ttl_sec());
  ASSERT_EQ(static_cast<size_t>(100), gt_config.max_redis_scan_records());
  ASSERT_EQ(false, gt_config.enable());
  ASSERT_EQ(10, gt_config.workers_cnt());
  ASSERT_EQ(std::chrono::minutes(5), gt_config.worker_max_wait_min());
  ASSERT_EQ(std::chrono::minutes(20), gt_config.worker_sleep_disable_min());
  ASSERT_EQ(10, gt_config.worker_cycle_cnt());
}
