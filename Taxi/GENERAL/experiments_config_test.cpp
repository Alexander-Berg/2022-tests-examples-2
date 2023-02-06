#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/experiments_config.hpp>

TEST(Experiments, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::Experiments& experiments_config =
      config.Get<config::Experiments>();

  const auto& config_versions_filter =
      experiments_config.experiments_launch_response_versions_filter;
  std::unordered_map<std::string, config::AppVersionsMap> empty_versions_filter;
  ASSERT_EQ(config_versions_filter, empty_versions_filter);
}
