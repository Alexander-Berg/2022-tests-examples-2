#include <gtest/gtest.h>
#include <fstream>
#include <optional>

#include <testing/source_path.hpp>
#include <userver/dynamic_config/fwd.hpp>
#include <userver/dynamic_config/snapshot.hpp>
#include <userver/dynamic_config/storage_mock.hpp>
#include <userver/dynamic_config/value.hpp>
#include <userver/formats/json/serialize.hpp>

#include <taxi_config/variables/TAXIMETER_VERSION_SETTINGS_BY_BUILD.hpp>
#include <taxi_config/variables/TAXIMETER_VERSION_SETTINGS_BY_ZONE.hpp>
#include <ua_parser/application.hpp>

#include <taximeter-version-settings/config.hpp>

namespace {

const std::string kVersionSettingsPath{"versionsettings.json"};
const std::string kZoneVersionSettingsPath{"zonesversionsettings.json"};
const std::string kApplicationDetectionRulesPath{"appdetector.json"};
const std::string kApplicationMapPath{"appmapbrand.json"};

namespace features {
const std::string kDefault{"default_feature"};
const std::string kAndroid{"android_bug_fix"};
const std::string kIos{"ios_feature"};
const std::string kFake{"fake_feature"};
}  // namespace features

formats::json::Value GetJsonConfig(const std::string& path) {
  return formats::json::blocking::FromFile(
      utils::CurrentSourcePath("src/tests/static/" + path));
}

dynamic_config::StorageMock GetConfig() {
  return {
      {taxi_config::TAXIMETER_VERSION_SETTINGS_BY_BUILD,
       GetJsonConfig(kVersionSettingsPath)},
      {taxi_config::TAXIMETER_VERSION_SETTINGS_BY_ZONE,
       GetJsonConfig(kZoneVersionSettingsPath)},
      ua_parser::LoadAppDetectorFromJson(
          GetJsonConfig(kApplicationDetectionRulesPath),
          GetJsonConfig(kApplicationMapPath)
              .As<dynamic_config::ValueDict<std::string>>()),
  };
}

TEST(TaximeterVersionSettings, MinVersion) {
  const auto config_storage = GetConfig();
  const auto config = config_storage.GetSnapshot();

  EXPECT_TRUE(taximeter_version_settings::IsTaximeterVersionAllowed(
      ua_parser::TaximeterApp::FromUserAgent("Taximeter 9.03"), config));

  EXPECT_FALSE(taximeter_version_settings::IsTaximeterVersionAllowed(
      ua_parser::TaximeterApp::FromUserAgent("Taximeter-Beta 9.05"), config));
  EXPECT_FALSE(taximeter_version_settings::IsTaximeterVersionAllowed(
      ua_parser::TaximeterApp::FromUserAgent("Taximeter-Beta 7.99"), config));

  EXPECT_TRUE(taximeter_version_settings::IsTaximeterVersionAllowed(
      ua_parser::TaximeterApp::FromUserAgent("Taximeter-Uber 1.10 (1234) ios"),
      config));
  EXPECT_FALSE(taximeter_version_settings::IsTaximeterVersionAllowed(
      ua_parser::TaximeterApp::FromUserAgent("Taximeter-Beta 1.99 (13) ios"),
      config));
}

TEST(TaximeterVersionSettings, MinVersionInZone) {
  const auto config_storage = GetConfig();
  const auto config = config_storage.GetSnapshot();

  EXPECT_TRUE(taximeter_version_settings::IsTaximeterVersionAllowedInZone(
      "moscow", ua_parser::TaximeterApp::FromUserAgent("Taximeter 7.03"),
      config));

  EXPECT_FALSE(taximeter_version_settings::IsTaximeterVersionAllowedInZone(
      "moscow", ua_parser::TaximeterApp::FromUserAgent("Taximeter 6.78"),
      config));

  EXPECT_FALSE(taximeter_version_settings::IsTaximeterVersionAllowedInZone(
      "moscow",
      ua_parser::TaximeterApp::FromUserAgent("Taximeter-Uber 7.1 (1234) ios"),
      config));
  EXPECT_TRUE(taximeter_version_settings::IsTaximeterVersionAllowedInZone(
      "moscow", ua_parser::TaximeterApp::FromUserAgent("Taximeter-Beta 6.78"),
      config));

  EXPECT_FALSE(taximeter_version_settings::IsTaximeterVersionAllowedInZone(
      "tula", ua_parser::TaximeterApp::FromUserAgent("Taximeter 7.03"),
      config));
}

TEST(TaximeterVersionSettings, FeatureSupport) {
  const auto config_storage = GetConfig();
  const auto config = config_storage.GetSnapshot();

  EXPECT_FALSE(taximeter_version_settings::IsFeatureEnabled(
      features::kFake,
      ua_parser::TaximeterApp::FromUserAgent("Taximeter-Beta 8.71 (1192)"),
      config));
  EXPECT_FALSE(taximeter_version_settings::IsFeatureEnabled(
      features::kIos,
      ua_parser::TaximeterApp::FromUserAgent("Taximeter-Beta 8.71 (1192)"),
      config));

  EXPECT_TRUE(taximeter_version_settings::IsFeatureEnabled(
      features::kDefault,
      ua_parser::TaximeterApp::FromUserAgent("Taximeter 8.80"), config));
  EXPECT_FALSE(taximeter_version_settings::IsFeatureEnabled(
      features::kDefault,
      ua_parser::TaximeterApp::FromUserAgent("Taximeter-Beta 8.80"), config));
}

TEST(TaximeterVersionSettings, FeatureVersion) {
  const auto config_storage = GetConfig();
  const auto config = config_storage.GetSnapshot();

  EXPECT_EQ(*taximeter_version_settings::GetFeatureVersion(features::kAndroid,
                                                           config),
            ua_parser::TaximeterVersion("9.00"));
  EXPECT_EQ(*taximeter_version_settings::GetFeatureVersion(features::kDefault,
                                                           config),
            ua_parser::TaximeterVersion("8.80"));
  EXPECT_EQ(
      *taximeter_version_settings::GetFeatureVersion(
          features::kDefault, config,
          ua_parser::TaximeterApp::FromUserAgent("Taximeter-Beta 8.71 (1192)")),
      ua_parser::TaximeterVersion("8.80 (13)"));
  EXPECT_EQ(
      taximeter_version_settings::GetFeatureVersion(features::kIos, config),
      std::nullopt);
  EXPECT_EQ(*taximeter_version_settings::GetFeatureVersion(
                features::kIos, config,
                ua_parser::TaximeterApp::FromUserAgent(
                    "Taximeter-Uber 9.1 (1234) ios")),
            ua_parser::TaximeterVersion("1.23 (123)"));
}

TEST(TaximeterVersionSettings, FeaturesSet) {
  const auto config_storage = GetConfig();
  const auto config = config_storage.GetSnapshot();

  auto features = taximeter_version_settings::GetAvailableFeatures(
      ua_parser::TaximeterApp::FromUserAgent("Taximeter-Beta 9.80 (1192)"),
      config);
  EXPECT_EQ(features,
            std::unordered_set<std::string>(
                {"android_bug_fix", "default_feature", "beta_feature"}));
  features = taximeter_version_settings::GetAvailableFeatures(
      ua_parser::TaximeterApp::FromUserAgent("Taximeter-Beta 8.71 (1192)"),
      config);
  EXPECT_EQ(features, std::unordered_set<std::string>({}));
  features = taximeter_version_settings::GetAvailableFeatures(
      ua_parser::TaximeterApp::FromUserAgent("Taximeter-Beta 8.80 (11)"),
      config);
  EXPECT_EQ(features, std::unordered_set<std::string>({}));
  features = taximeter_version_settings::GetAvailableFeatures(
      ua_parser::TaximeterApp::FromUserAgent("Taximeter-Beta 9.01"), config);
  EXPECT_EQ(features, std::unordered_set<std::string>(
                          {"android_bug_fix", "default_feature"}));
}

}  // namespace
