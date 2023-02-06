#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/corp_integration_config.hpp>

TEST(CorpIntegrationConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& corp_integration_config = config.Get<config::CorpIntegration>();
  ASSERT_EQ(corp_integration_config.client_timeout, 100);
  ASSERT_EQ(corp_integration_config.client_retries, 3);
  ASSERT_EQ(corp_integration_config.paymentmethods_enabled, false);
  ASSERT_EQ(corp_integration_config.multiclass_corp_flow_enabled, false);
}
