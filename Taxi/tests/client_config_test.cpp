#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/client_config.hpp>
#include <config/config.hpp>
#include <config/value_with_default.hpp>

TEST(DriverRatingsClient, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& test_config = config.Get<config::DriverRatingsClient>();
  using config::GetOrDefault;
  ASSERT_EQ(test_config.timeout_retries.size(), 1u);
  ASSERT_EQ(GetOrDefault(test_config.timeout_retries, "c").size(), 1u);
  ASSERT_EQ(GetOrDefault(GetOrDefault(test_config.timeout_retries, "c"), "url")
                .timeout_ms.count(),
            250u);
  ASSERT_EQ(GetOrDefault(GetOrDefault(test_config.timeout_retries, "c"), "url")
                .retries,
            3);
}
