#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/complement_payment_config.hpp>
#include <config/config.hpp>

TEST(TestComplementPaymentConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& complement_payment_config =
      config.Get<config::ComplementPaymentConfig>();

  const auto& payment_types =
      complement_payment_config.complement_types_compatibility.Get(
          "personal_wallet");
  ASSERT_TRUE(payment_types);
  ASSERT_EQ(3U, payment_types->size());
  ASSERT_EQ((config::PaymentTypes{models::payment_types::Card,
                                  models::payment_types::ApplePay,
                                  models::payment_types::GooglePay}),
            payment_types);
  const auto& minimal_balance =
      complement_payment_config
          .personal_wallet_complement_branding_minimal_balance.Get("RUB");
  ASSERT_TRUE(minimal_balance);
  ASSERT_DOUBLE_EQ(50, *minimal_balance);
}
