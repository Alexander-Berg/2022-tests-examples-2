#include <gtest/gtest.h>

#include <modules/zoneinfo-core/category_filters.hpp>
#include <testing/taxi_config.hpp>

namespace zoneinfo::core {

namespace {

std::vector<clients::taxi_tariffs::Category> MockCategories() {
  clients::taxi_tariffs::Category econom;
  econom.name = "econom";
  clients::taxi_tariffs::Category uberx;
  uberx.name = "uberx";
  clients::taxi_tariffs::Category cargo;
  cargo.name = "cargo";
  clients::taxi_tariffs::Category ultima;
  ultima.name = "ultima";
  clients::taxi_tariffs::Category selfdriving;
  selfdriving.name = "selfdriving";
  return {econom, cargo, ultima, selfdriving};
}

using SkippedFlagByCategories = std::unordered_map<std::string, bool>;
SkippedFlagByCategories MockSkippedFlagByCategories() {
  return {{"econom", false},
          {"uberx", true},
          {"cargo", false},
          {"ultima", false},
          {"selfdriving", false}};
}

taxi_config::TaxiConfig MockConfig() {
  auto taxi_config =
      dynamic_config::GetDefaultSnapshot().Get<taxi_config::TaxiConfig>();

  // ZONEINFO_TARIFFS_SETTINGS_BY_MODES_IN_ZONES
  std::vector<std::string> ultima_modes = {"default", "ultima"};
  std::vector<std::string> sdc_modes = {"sdc"};
  std::unordered_map<std::string, ::std::vector<std::string>> modes_map = {
      {"ultima", ultima_modes}, {"selfdriving", sdc_modes}};
  taxi_config.zoneinfo_tariffs_settings_by_modes_in_zones.extra = {
      {"moscow", {modes_map}}};

  // ZONEINFO_FALLBACK_IGNORED_TARIFFS
  taxi_config.zoneinfo_fallback_ignored_tariffs = {"cargo"};
  return taxi_config;
}

}  // namespace

TEST(TestCategoryFilters, All) {
  auto taxi_config = MockConfig();
  const auto& ts_categories = MockCategories();
  const auto& skipped_flag_by_categories = MockSkippedFlagByCategories();
  const auto& result = FilterCategories(
      ts_categories, skipped_flag_by_categories, taxi_config, "moscow");
  ASSERT_EQ(result.size(), 2);
  ASSERT_EQ(result[0].name, "econom");
  ASSERT_EQ(result[1].name, "ultima");
}

}  // namespace zoneinfo::core
