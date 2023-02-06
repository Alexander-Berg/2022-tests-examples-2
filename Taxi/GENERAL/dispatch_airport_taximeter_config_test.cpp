#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>

#include "dispatch_airport_taximeter_config.hpp"

TEST(TestDispatchAirportTaximeterConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& cfg = config.Get<config::DispatchAirportTaximeterConfig>();

  ASSERT_EQ(std::chrono::minutes(10),
            cfg.taximeter_config->min_etr_minutes_to_show);
  ASSERT_EQ(std::chrono::hours(3), cfg.taximeter_config->max_etr_hours_to_show);
  ASSERT_EQ(size_t{5}, cfg.taximeter_config->position_step);

  const auto& dialog = cfg.taximeter_config->dialogs["any_dialog"];
  ASSERT_EQ("overlay_notification", dialog.type);
  ASSERT_EQ(false, !!dialog.affirmative_button_key);
  ASSERT_EQ(false, !!dialog.negative_button_key);
  ASSERT_EQ("info", dialog.severity);
}
