#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/dadata.hpp>

TEST(TestDadataConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& test_config = config.Get<config::Dadata>();
  ASSERT_EQ(2, test_config.retries);
  ASSERT_EQ(1000, test_config.timeout_ms->count());
}
