#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/driver_protocol_client.hpp>

TEST(DriverProtocolClient, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& dp_client = config.Get<config::DriverProtocolClient>();
  ASSERT_EQ(dp_client.timeout_retries().size(), 1u);
  ASSERT_EQ(dp_client.timeout_retries["some_handler"].timeout_ms.count(),
            1000u);
  ASSERT_EQ(dp_client.timeout_retries["some_handler"].retries, 3);
}
