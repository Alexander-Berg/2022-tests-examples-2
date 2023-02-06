#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/referral_config.hpp>

TEST(TestReferralConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& referral_config = config.Get<config::ReferralConfig>();
  ASSERT_EQ(5u, referral_config.count);
}
