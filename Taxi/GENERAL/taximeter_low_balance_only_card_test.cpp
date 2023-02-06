#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/taximeter_low_balance_only_card.hpp>

TEST(TestTaximeterLowBalanceOnlyCard, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& taximeter_low_balance_only_card =
      config.Get<config::TaximeterLowBalanceOnlyCard>();
  ASSERT_EQ(taximeter_low_balance_only_card.enable, true);
}
