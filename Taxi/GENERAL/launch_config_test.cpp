#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/launch_config.hpp>

TEST(TestLaunchConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::Launch& launch_config = config.Get<config::Launch>();
  ASSERT_EQ(launch_config.ask_feedback_timeout, 86400);
}
