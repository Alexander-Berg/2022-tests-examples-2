#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>

#include "config.hpp"

TEST(TestTrackerClientConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::TrackerClientConfig& tracker_config =
      config.Get<config::TrackerClientConfig>();

  ASSERT_TRUE(tracker_config.request_shorttracks_via_flatbuffers);
  ASSERT_EQ(tracker_config.nearest_drivers_bulk_max_size, 0u);

  ASSERT_EQ(tracker_config.tracker_request_settings.GetMap().size(), 2u);
}
