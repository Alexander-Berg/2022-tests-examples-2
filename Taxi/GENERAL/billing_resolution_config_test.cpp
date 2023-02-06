#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/billing_resolution_config.hpp>
#include <config/config.hpp>

TEST(TestBillingResolutionConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::BillingResolution& billing_resolution_config =
      config.Get<config::BillingResolution>();

  ASSERT_EQ(billing_resolution_config.creditcard_enabled.Get(), true);
  ASSERT_EQ(billing_resolution_config.corp_enabled.Get(), true);
  ASSERT_EQ(billing_resolution_config.personal_wallet_enabled.Get(), false);
  ASSERT_EQ(billing_resolution_config.coop_account_enabled.Get(), false);
}
