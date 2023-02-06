#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/zoneinfo_config.hpp>
#include <utils/jsonfixtures.hpp>

TEST(TestOrderForOther, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::ZoneInfo& zi_cfg = config.Get<config::ZoneInfo>();

  const auto& order_for_other = zi_cfg.order_for_other.Get("__default__");

  EXPECT_TRUE(order_for_other.get().include);
}

TEST(TestTariffSettingsByModesInZones, StandardParsingConfig) {
  const auto& tariff_settings_by_modes_in_zones_bson =
      JSONFixtures::GetFixtureBSON(
          "tariff_setting_by_modes_in_zones_parse.json");
  const auto tariff_settings_by_modes_in_zones =
      config::ParseTariffSettingsByModesInZones(
          tariff_settings_by_modes_in_zones_bson
              ["ZONEINFO_TARIFFS_SETTINGS_BY_MODES_IN_ZONES"]);

  const auto default_zone =
      tariff_settings_by_modes_in_zones.Get("default_zone");
  EXPECT_FALSE(default_zone.is_initialized());
  const auto& skolkovo_zone_opt =
      tariff_settings_by_modes_in_zones.Get("skolkovo");
  EXPECT_TRUE(skolkovo_zone_opt.is_initialized());
  const auto& skolkovo_zone = skolkovo_zone_opt.get();
  ASSERT_EQ(skolkovo_zone.count("selfdriving"), 1u);
  ASSERT_EQ(skolkovo_zone.at("selfdriving").size(), 1u);
  ASSERT_EQ(skolkovo_zone.at("selfdriving").front(), "sdc");
  const auto& test_zone_opt =
      tariff_settings_by_modes_in_zones.Get("test_zone");
  EXPECT_TRUE(test_zone_opt.is_initialized());
  const auto& test_zone = test_zone_opt.get();
  ASSERT_EQ(test_zone.count("test_category"), 1u);
  ASSERT_EQ(test_zone.at("test_category").size(), 3u);
  ASSERT_EQ(test_zone.at("test_category").front(), "test_mode");
  ASSERT_EQ(test_zone.count("test_category_2"), 1u);
  ASSERT_EQ(test_zone.at("test_category_2").size(), 0u);
}
