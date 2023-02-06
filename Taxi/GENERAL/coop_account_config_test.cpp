#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/coop_account_config.hpp>

TEST(TestCoopAccountConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& coop_account_config = config.Get<config::CoopAccountConfig>();

  const auto& brands = coop_account_config.non_ignore_debt_by_brand.Get();
  std::unordered_set<std::string> expected_brands({"yango", "yataxi"});
  EXPECT_EQ(brands, expected_brands);

  ASSERT_EQ(coop_account_config.check_available.Get(), false);
}
