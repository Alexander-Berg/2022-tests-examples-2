#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/billing_component_config.hpp>
#include <config/config.hpp>

TEST(TestBillingComponentConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::BillingComponent& bc_config =
      config.Get<config::BillingComponent>();

  ASSERT_EQ(bc_config.service_url.Get(),
            "http://greed-tm1f.yandex.ru:8018/simple/xmlrpc");
  ASSERT_EQ(bc_config.requests_timeout_ms.Get(), 5000u);
  ASSERT_EQ(bc_config.requests_fallback_timeout_ms.Get(), 500u);
  ASSERT_EQ(bc_config.pass_region_id.Get(), false);
  ASSERT_EQ(bc_config.receipt_url.Get(),
            "https://trust.yandex.ru/receipts/{}-{}/");
  ASSERT_EQ(bc_config.receipt_pdf_suffix.Get(), "?mode=pdf");
}
