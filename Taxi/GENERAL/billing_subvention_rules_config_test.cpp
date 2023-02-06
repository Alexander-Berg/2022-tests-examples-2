#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/billing_subvention_rules_config.hpp>
#include <config/config.hpp>

TEST(TestBillingSubventionRulesConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& billing_subvention_rules_config =
      config.Get<config::BillingSubventionRules>();
  ASSERT_EQ(billing_subvention_rules_config
                .cache_billing_subvention_rules_update_enabled,
            false);
  ASSERT_EQ(billing_subvention_rules_config.handles_use_client_over_cache.Get()
                .size(),
            0ul);
}
