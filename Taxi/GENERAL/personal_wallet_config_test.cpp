#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/personal_wallet_config.hpp>

TEST(TestPersonalWalletConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& personal_wallet_config =
      config.Get<config::PersonalWalletConfig>();
  ASSERT_EQ(personal_wallet_config.currency_rules.size(), 1u);

  auto& currency_rule = personal_wallet_config.currency_rules[0];
  ASSERT_EQ(currency_rule.currency, "RUB");
  ASSERT_EQ(currency_rule.country_code, "rus");

  ASSERT_EQ(currency_rule.payment_methods.size(), 3u);
  auto payment_methods_begin = currency_rule.payment_methods.begin();
  auto payment_methods_end = currency_rule.payment_methods.end();
  ASSERT_TRUE(std::find(payment_methods_begin, payment_methods_end, "card") !=
              payment_methods_end);
  ASSERT_TRUE(std::find(payment_methods_begin, payment_methods_end,
                        "applepay") != payment_methods_end);
  ASSERT_TRUE(std::find(payment_methods_begin, payment_methods_end,
                        "googlepay") != payment_methods_end);

  ASSERT_EQ(currency_rule.phone_patterns.size(), 1u);
  ASSERT_EQ(currency_rule.phone_patterns[0], "+79");

  ASSERT_EQ(currency_rule.exclude_patterns.size(), 4u);
  auto exclude_patterns_begin = currency_rule.exclude_patterns.begin();
  auto exclude_patterns_end = currency_rule.exclude_patterns.end();
  ASSERT_TRUE(std::find(exclude_patterns_begin, exclude_patterns_end,
                        "+7940") != payment_methods_end);
  ASSERT_TRUE(std::find(exclude_patterns_begin, exclude_patterns_end,
                        "+7995344") != payment_methods_end);
  ASSERT_TRUE(std::find(exclude_patterns_begin, exclude_patterns_end,
                        "+7997") != payment_methods_end);
  ASSERT_TRUE(std::find(exclude_patterns_begin, exclude_patterns_end,
                        "+7998") != payment_methods_end);

  ASSERT_TRUE(currency_rule.show_to_new_users);
  ASSERT_FALSE(personal_wallet_config.show_discount_mocks);
  ASSERT_FALSE(
      personal_wallet_config.disable_payment_personal_wallet_if_no_ya_plus);
}
