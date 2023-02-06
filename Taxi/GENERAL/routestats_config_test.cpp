#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/routestats_config.hpp>

TEST(Routestats, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::Routestats& routestats_config =
      config.Get<config::Routestats>();

  ASSERT_DOUBLE_EQ(
      1.6, routestats_config.surge_color_button_min_value_zone.Get().Get());
  ASSERT_DOUBLE_EQ(1.25,
                   routestats_config.surge_high_demand_min_value_zone.Get());
  ASSERT_DOUBLE_EQ(2.5,
                   routestats_config.surge_popup_min_coeff_zone.Get().Get());

  ASSERT_EQ(4U, routestats_config.paid_supply_min_versions.size());
  ASSERT_EQ("8.73",
            routestats_config.paid_supply_min_taximeter_version->ToString());

  ASSERT_FALSE(routestats_config.fetch_candidates_from_tracker);
  ASSERT_TRUE(routestats_config.price_promo_suggest_classes.empty());
  ASSERT_TRUE(
      routestats_config.zones_using_original_price_with_free_route->empty());
  ASSERT_FALSE(routestats_config.paid_supply_for_decoupling_enabled);
  const auto& excluded_clients =
      routestats_config.paid_supply_for_decoupling_excluded_clients.Get();
  ASSERT_TRUE(excluded_clients.empty());
}
