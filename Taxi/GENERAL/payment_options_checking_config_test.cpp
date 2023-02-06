#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/payment_options_checking_config.hpp>

TEST(TestPaymentOptionCheckingConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& payment_options_checking_config =
      config.Get<config::PaymentOptionCheckingConfig>();

  ASSERT_FALSE(
      payment_options_checking_config.check_payment_options_in_orderdraft);
  ASSERT_FALSE(
      payment_options_checking_config.use_card_like_routestats_request);
}
