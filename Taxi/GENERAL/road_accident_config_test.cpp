#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/road_accident_config.hpp>

TEST(TestRoadAccidenetConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::RoadAccident& road_accident_config =
      config.Get<config::RoadAccident>();

  ASSERT_EQ(road_accident_config.backend.allow_no_order, false);

  ASSERT_EQ(
      road_accident_config.accelerometer.log_duration_after_accident_millis,
      static_cast<std::uint32_t>(5000));
}
