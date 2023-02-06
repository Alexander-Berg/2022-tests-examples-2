#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/car_numbers_format.hpp>
#include <config/config.hpp>

TEST(TestCarNumberFormat, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& test_config = config.Get<config::CarNumberFormat>();

  ASSERT_TRUE(test_config.info_map.empty());
}
