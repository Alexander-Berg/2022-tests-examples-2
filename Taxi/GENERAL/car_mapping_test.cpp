#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>

#include "car_mapping_config.hpp"

TEST(TestCarMapping, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::CarMapping& local_config = config.Get<config::CarMapping>();

  ASSERT_TRUE(local_config.car_mark_display_rules.empty());
}
