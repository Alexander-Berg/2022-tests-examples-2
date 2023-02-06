#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/taximeter_client.hpp>

TEST(TestTaximeterClientConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& test_config = config.Get<config::TaximeterClient>();
  ASSERT_EQ(test_config.timeout_retries().size(), 1u);

  ASSERT_EQ(test_config.timeout_retries["some_handler"].timeout_ms.count(),
            1000u);
  ASSERT_EQ(test_config.timeout_retries["some_handler"].retries, 3);

  ASSERT_EQ("taximeter-xservice", test_config.tvm2_service_name.Get());
}
