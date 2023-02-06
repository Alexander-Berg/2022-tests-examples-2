#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/payment_config.hpp>

TEST(TestPaymentConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& payment_config = config.Get<config::Payment>();

  ASSERT_EQ(payment_config.fallback_to_taximeter_on_calculator_error, false);
  ASSERT_EQ(payment_config.allow_change_to_cash_if_unsuccessful_payment, false);
  ASSERT_EQ(payment_config.fix_trust_ids_in_last_payment_method, false);
  ASSERT_EQ(payment_config.paymentmethods_iphone_merchant_list.Get().size(),
            0u);
  ASSERT_EQ(payment_config.paymentmethods_int_api_applepay_parameters_enabled,
            false);
}
