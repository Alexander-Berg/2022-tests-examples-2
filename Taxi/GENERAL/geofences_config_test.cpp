#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/geofences_config.hpp>

TEST(TestGeofencesConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::Geofences& geofences_config = config.Get<config::Geofences>();
  ASSERT_EQ(geofences_config.enabled, true);
}
