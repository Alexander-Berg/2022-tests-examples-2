#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/geofence_config.hpp>

TEST(TestGeofenceConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::Geofence& geofence_config = config.Get<config::Geofence>();
  ASSERT_EQ(geofence_config.output_error_retries, 3);
}
