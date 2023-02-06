#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include "road_accident_check_config.hpp"

TEST(TestRoadAccidentConfirmConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& road_accident_config = config.Get<config::RoadAccidentCheck>();
  ASSERT_EQ(static_cast<int>(road_accident_config.stop_check_after_second),
            600);
}
