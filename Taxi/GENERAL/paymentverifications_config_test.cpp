#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include "paymentverifications_config.hpp"

TEST(TestPaymentVerificationConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::PaymentVerifications& pv_config =
      config.Get<config::PaymentVerifications>();

  ASSERT_EQ(
      pv_config.card_binding_trust_error_code_to_translation_error_code_map
          .Get(),
      "card_binding_error_message.refer_to_support");
}
