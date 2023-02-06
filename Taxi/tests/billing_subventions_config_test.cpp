#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>

#include <clients/billing_subventions_config.hpp>

TEST(TestBillingSubventionsConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& bs_config = config.Get<config::BillingSubventions>();

  ASSERT_EQ(bs_config.client.url, "http://billing-subventions.taxi.yandex.net");
  ASSERT_EQ(bs_config.client.retry, 3u);
  ASSERT_EQ(bs_config.client.timeout, std::chrono::milliseconds(500));
  ASSERT_EQ(bs_config.client.rules_select_limit, 1000u);

  ASSERT_EQ(bs_config.client.lru_cache_enabled, false);
  ASSERT_EQ(bs_config.client.cache_expiration, std::chrono::seconds(60));
  ASSERT_EQ(bs_config.client.cache_max_size, 1000ul);
  ASSERT_EQ(bs_config.client.time_tolerance, std::chrono::seconds(60));
}
