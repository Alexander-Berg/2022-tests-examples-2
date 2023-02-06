#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/surge_client_params.hpp>

TEST(TestSurgeClientParams, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& surge_client_params = config.Get<config::SurgeClientParams>();
  ASSERT_EQ(0u, surge_client_params.max_speed);
}
