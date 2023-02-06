#include <gtest/gtest.h>

#include <exception>

#include <userver/dynamic_config/fwd.hpp>
#include <userver/dynamic_config/snapshot.hpp>
#include <userver/dynamic_config/value.hpp>
#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value_builder.hpp>

#include <feature-settings-configs/park.hpp>

namespace {

const std::string kConfigName{"TAXIMETER_CATEGORY_SETTINGS"};

formats::json::Value GetDisabledFeatureSettings() {
  constexpr const char* kDoc = "{\"dbs\":[\"Park0\"],\"enable\":false}";
  return formats::json::FromString(kDoc);
}

formats::json::Value GetEnabledFeatureSettingsWithEmptyArrays() {
  constexpr const char* kDoc = "{\"dbs\":[],\"enable\":true}";
  return formats::json::FromString(kDoc);
}

formats::json::Value GetEnabledFeatureSettingsWithSomeDisabled() {
  constexpr const char* kDoc =
      "{\"dbs\":[],\"dbs_disable\":[\"Park1\"],\"enable\":true}";
  return formats::json::FromString(kDoc);
}

formats::json::Value GetEnabledFeatureSettingsWithSomeEnabledSomeDisabled() {
  constexpr const char* kDoc =
      "{\"dbs\":[\"Park0\",\"Park1\"],\"dbs_disable\":[\"Park1\"],\"enable\":"
      "true}";
  return formats::json::FromString(kDoc);
}

dynamic_config::DocsMap GetDocsMap(const formats::json::Value& value) {
  dynamic_config::DocsMap docs_map;
  docs_map.Set(kConfigName, value);
  return docs_map;
}

TEST(ParkCityCountryFeature, Disabled) {
  dynamic_config::DocsMap docs_map{GetDocsMap(GetDisabledFeatureSettings())};

  feature_settings_configs::park::Config config(docs_map);

  // disabled because of "enable":false, park means nothing
  EXPECT_FALSE(config.IsEnabled("Park0", kConfigName));
  EXPECT_FALSE(config.IsEnabled("Park1", kConfigName));

  // exception because of wrong config name
  EXPECT_THROW(config.IsEnabled("Park0", "._."), std::runtime_error);
}

TEST(ParkCityCountryFeature, EnabledEmptyArrays) {
  dynamic_config::DocsMap docs_map{
      GetDocsMap(GetEnabledFeatureSettingsWithEmptyArrays())};

  feature_settings_configs::park::Config config(docs_map);

  // enabled because of "enable":true, park means nothing, because
  // arrays are empty
  EXPECT_TRUE(config.IsEnabled("Park0", kConfigName));

  // exception because of wrong config name
  EXPECT_THROW(config.IsEnabled("Park0", "._."), std::runtime_error);
}

TEST(ParkCityCountryFeature, AllEnabledExceptDisabled) {
  dynamic_config::DocsMap docs_map{
      GetDocsMap(GetEnabledFeatureSettingsWithSomeDisabled())};

  feature_settings_configs::park::Config config(docs_map);

  // enabled except ones in "_disable" arrays
  EXPECT_TRUE(config.IsEnabled("Park0", kConfigName));
  EXPECT_FALSE(config.IsEnabled("Park1", kConfigName));
  EXPECT_TRUE(config.IsEnabled("Whatever", kConfigName));

  // exception because of wrong config name
  EXPECT_THROW(config.IsEnabled("Park0", "._."), std::runtime_error);
}

TEST(ParkCityCountryFeature, SomeEnabledExceptDisabled) {
  dynamic_config::DocsMap docs_map{
      GetDocsMap(GetEnabledFeatureSettingsWithSomeEnabledSomeDisabled())};

  feature_settings_configs::park::Config config(docs_map);

  // enabled if value in main array and not in "_disable" array
  EXPECT_TRUE(config.IsEnabled("Park0", kConfigName));
  EXPECT_FALSE(config.IsEnabled("Park1", kConfigName));
  EXPECT_FALSE(config.IsEnabled("Whatever", kConfigName));

  // exception because of wrong config name
  EXPECT_THROW(config.IsEnabled("Park0", "._."), std::runtime_error);
}

}  // namespace
