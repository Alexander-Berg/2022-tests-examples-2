#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>

#include "chain_config.hpp"

TEST(TestChainConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::Chain& chain_config = config.Get<config::Chain>();

  ASSERT_EQ(chain_config.driver_destination_info_to_logbroker, false);
  ASSERT_EQ(chain_config.driver_weariness_multi_app_drivers_enabled, false);
  ASSERT_EQ(
      chain_config.driver_weariness_mad_max_work_time.GetDefault().count(),
      720);
  ASSERT_EQ(chain_config.driver_weariness_work_rest_enabled, false);
  ASSERT_EQ(chain_config.driver_weariness_work_rest_time.Get().count(), 480);
  ASSERT_EQ(chain_config.driver_weariness_mad_returned_driver_ids.Get().size(),
            0u);
  ASSERT_EQ(
      chain_config.driver_weariness_status_free_no_wove_time.Get().count(), 10);
  ASSERT_EQ(chain_config.tracker_process_logbroker_threads_num.Get(), 4u);
  ASSERT_EQ(chain_config.tracker_navigator_max_cord_time_diff.Get().count(),
            90);
  ASSERT_TRUE(chain_config.labor_busy_drivers_worker_enabled);
}
