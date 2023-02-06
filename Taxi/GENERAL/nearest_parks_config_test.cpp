#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/nearest_parks_config.hpp>

TEST(TestNearestParksConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::NearestParksConfig& nearest_parks_config =
      config.Get<config::NearestParksConfig>();

  ASSERT_EQ(nearest_parks_config.partners_allowed_countries.Get().size(), 1u);
}
