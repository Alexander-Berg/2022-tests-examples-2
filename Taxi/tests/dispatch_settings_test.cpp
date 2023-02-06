#include <gtest/gtest.h>

#include <models/dispatch_settings.hpp>
#include <models/dispatch_settings_model.hpp>

namespace {

const std::string kDefault = "__default__";

}  // namespace

namespace {

models::SettingsValues CreateFallback() {
  models::SettingsValues values;
  values.query_limit_free_preferred = 1;
  values.query_limit_limit = 2;
  values.query_limit_max_line_dist = 3;
  return values;
}

models::DispatchSettingsModelMap CreateSettings() {
  models::DispatchSettingsModelMap data;
  {
    models::SettingsKey key{};
    key.zone_name = "test_zone_1";
    key.tariff_name = "econom";
    models::SettingsValues values;
    values.query_limit_free_preferred = 100;
    values.query_limit_limit = 200;
    values.query_limit_max_line_dist = 300;
    data[key] = std::move(values);
  }
  {
    models::SettingsKey key{};
    key.zone_name = kDefault;
    key.tariff_name = "__default__base__";
    models::SettingsValues values;
    values.query_limit_free_preferred = 1000;
    values.query_limit_limit = 2000;
    values.query_limit_max_line_dist = 3000;
    data[key] = std::move(values);
  }
  return data;
}

}  // namespace

TEST(DispatchSettingsModel, ModelTest) {
  models::DispatchSettingsModelMap data = CreateSettings();
  ASSERT_EQ(data.size(), 2u);

  models::SettingsKey key{};
  key.zone_name = "test_zone_1";
  key.tariff_name = "econom";
  auto it = data.find(key);
  ASSERT_NE(it, data.end());
  models::SettingsValues& values = it->second;
  ASSERT_EQ(values.query_limit_free_preferred, 100u);
  ASSERT_EQ(values.query_limit_limit, 200u);
  ASSERT_EQ(values.query_limit_max_line_dist, 300u);
}

TEST(DispatchSettingsModel, GroupSettingsTest) {
  models::TariffGroups tariff_groups{{"econom", "base"}, {"business", "base"}};
  dispatch_settings::DispatchSettings settings{
      models::TariffGroups{tariff_groups}, CreateSettings(), CreateFallback()};

  dispatch_settings::DispatchSettings::FetchDeps deps;
  // regular settings
  deps.zone_name = "test_zone_1";
  deps.tariff_name = "econom";
  auto values = settings.Fetch(deps);

  ASSERT_EQ(values.query_limit_free_preferred, 100u);
  ASSERT_EQ(values.query_limit_limit, 200u);
  ASSERT_EQ(values.query_limit_max_line_dist, 300u);

  deps.zone_name = "test_zone_1";
  deps.tariff_name = "business";
  // fallback to __default__base__
  values = settings.Fetch(deps);

  ASSERT_EQ(values.query_limit_free_preferred, 1000u);
  ASSERT_EQ(values.query_limit_limit, 2000u);
  ASSERT_EQ(values.query_limit_max_line_dist, 3000u);

  dispatch_settings::DispatchSettings settings_without_fallback{
      models::TariffGroups{tariff_groups}, CreateSettings(), CreateFallback()};
  deps.zone_name = "test_zone_1";
  deps.tariff_name = "any";
  // fallback
  values = settings_without_fallback.Fetch(deps);

  ASSERT_EQ(values.query_limit_free_preferred, 1u);
  ASSERT_EQ(values.query_limit_limit, 2u);
  ASSERT_EQ(values.query_limit_max_line_dist, 3u);
}
