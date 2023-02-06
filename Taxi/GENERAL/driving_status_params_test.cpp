#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/driving_status_params.hpp>

TEST(TestDrivingStatusParams, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& driving_status_params = config.Get<config::DrivingStatusParams>();

  ASSERT_EQ(200.0, driving_status_params.map_activation_distance);
  ASSERT_EQ(1000u, driving_status_params.open_navi_delay_ms);
  ASSERT_EQ(10000l, driving_status_params.update_navi_passengers_millis);
  ASSERT_EQ(600.0, driving_status_params.meters_delta_to_passenger);
  ASSERT_EQ(120000l, driving_status_params.outdated_passenger_delta_millis);
}
