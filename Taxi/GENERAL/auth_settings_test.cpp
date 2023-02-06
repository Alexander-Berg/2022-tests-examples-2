#include "auth_settings.hpp"

#include <gtest/gtest.h>
#include <chrono>

#include <common/test_config.hpp>
#include <config/config.hpp>

TEST(TestClassesPriorityOrdered, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& auth_config = config.Get<config::Auth>();
  ASSERT_EQ(auth_config.session_ttl.Get(), std::chrono::seconds(7200));
}
