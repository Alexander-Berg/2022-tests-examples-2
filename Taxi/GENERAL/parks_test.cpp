#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/parks.hpp>

TEST(TestParksConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& test_config = config.Get<config::Parks>();
  EXPECT_TRUE(test_config.enable_photo_validity_check);
  EXPECT_EQ(0u, test_config.car_minimum_manufactured_year);
}
