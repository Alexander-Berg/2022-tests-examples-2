#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/multiorder_config.hpp>

TEST(TestMultiorderConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::MultiorderConfig& multiorder_config =
      config.Get<config::MultiorderConfig>();

  ASSERT_EQ(multiorder_config.numeral_threshold_count, 3);
}
