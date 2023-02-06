#include "user_tracker_config.hpp"

#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>

TEST(UserTrackerConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& ut_config = config.Get<config::UserTracker>();
  ASSERT_EQ(900u, ut_config.max_age_sec());
}
