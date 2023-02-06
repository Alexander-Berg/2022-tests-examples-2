#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/agglomerations_config.hpp>
#include <config/config.hpp>

TEST(TestAgglomerationsConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& agglomerations_config = config.Get<config::Agglomerations>();

  ASSERT_EQ(agglomerations_config.cache_agglomerations_update_enabled, false);
}
