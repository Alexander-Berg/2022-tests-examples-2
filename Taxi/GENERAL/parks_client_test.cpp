#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/parks_client.hpp>

TEST(TestParksClientConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& test_config = config.Get<config::ParksClient>();
  ASSERT_EQ(test_config.timeout_retries().size(), 1u);

  ASSERT_EQ(test_config.timeout_retries["some_handler"].timeout_ms.count(),
            1000u);
  ASSERT_EQ(test_config.timeout_retries["some_handler"].retries, 2);

  ASSERT_EQ("parks", test_config.tvm2_service_name.Get());
}
