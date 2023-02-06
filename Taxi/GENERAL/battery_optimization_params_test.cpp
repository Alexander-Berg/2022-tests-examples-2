#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/battery_optimization_params.hpp>
#include <config/config.hpp>

TEST(TestBatteryOptimizationParams, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& battery_optimization_params =
      config.Get<config::BatteryOptimizationParams>();
  ASSERT_EQ(std::chrono::seconds(30),
            battery_optimization_params.delay_to_process_seconds);
}
