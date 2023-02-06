#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/payment_methods_config.hpp>

TEST(TestPaymentMethodsConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& payment_methods_config =
      config.Get<config::PaymentMethodsConfig>();

  const auto& default_payment_methods =
      payment_methods_config.allowed_payment_types_for_requirements
          .GetDefaultValue();
  ASSERT_TRUE(default_payment_methods.allowed_by_default);
  ASSERT_TRUE(default_payment_methods.non_default_payment_types.empty());
}
