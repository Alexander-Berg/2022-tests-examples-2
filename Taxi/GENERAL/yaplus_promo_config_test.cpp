#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/yaplus_promo_config.hpp>

TEST(TestYaPlusPromoConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);

  const auto& yaplus_cfg = config.Get<config::YaPlusSummaryPromo>();
  ASSERT_EQ(yaplus_cfg.enabled, false);

  const auto& coutry_config = yaplus_cfg.settings["ru"];
  ASSERT_EQ(coutry_config.content.size(), 0u);
  ASSERT_EQ(*coutry_config.action.url, "");
}
