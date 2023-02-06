#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/multiclass_config.hpp>

TEST(TestMulticlassConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::MulticlassConfig& multiclass_config =
      config.Get<config::MulticlassConfig>();

  ASSERT_EQ(multiclass_config.enabled, true);
  ASSERT_EQ(multiclass_config.default_enabled, true);

  const auto& popup_show_rules = multiclass_config.popup_show_rules;
  ASSERT_EQ(popup_show_rules.show_count, 3);

  ASSERT_EQ(popup_show_rules.show_rules.size(), 1u);
  const auto& rule = popup_show_rules.show_rules[0];
  ASSERT_EQ(rule.count, 3);
  ASSERT_EQ(rule.metric, "tariff_switch");
  ASSERT_EQ(rule.period_seconds, 8);
}
