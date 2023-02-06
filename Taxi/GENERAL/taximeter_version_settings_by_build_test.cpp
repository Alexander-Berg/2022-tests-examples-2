#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/taximeter_version_settings_by_build.hpp>
#include <models/configs.hpp>
#include <utils/taximeter_application.hpp>

namespace {

using App = models::TaximeterApp;
using Version = models::TaximeterVersion;
using Type = models::TaximeterVersionType;
using Platform = models::TaximeterPlatform;

const std::string kMin{"min"};
const std::string kCurrent{"current"};
const std::string kDisabled{"disabled"};
const std::string kFeatureSupport{"feature_support"};
const std::string kConfigName{"TAXIMETER_VERSION_SETTINGS_BY_BUILD"};

static const auto taximeter_version_by_build{[]() {
  // default
  Json::Value default_section{Json::objectValue};
  default_section[kMin] = "8.78";
  default_section[kCurrent] = "9.00";

  Json::Value default_disabled{Json::arrayValue};
  default_disabled.append("8.98");
  default_section[kDisabled] = std::move(default_disabled);

  Json::Value default_fs{Json::objectValue};
  default_fs["default_1"] = "8.70";
  default_fs["default_2"] = "8.95";
  default_section[kFeatureSupport] = std::move(default_fs);

  // production
  Json::Value production_section{Json::objectValue};
  production_section[kMin] = "8.80";
  production_section[kCurrent] = "9.05";

  Json::Value production_disabled{Json::arrayValue};
  production_disabled.append("9.02");
  production_section[kDisabled] = std::move(production_disabled);

  Json::Value production_fs{Json::objectValue};
  production_fs["production_1"] = "8.72";
  production_fs["default_2"] = "8.90";  // overrides down
  production_section[kFeatureSupport] = std::move(production_fs);

  // yango
  Json::Value yango_section{Json::objectValue};
  yango_section[kMin] = "8.95";
  yango_section[kCurrent] = "9.10";

  Json::Value yango_disabled{Json::arrayValue};
  yango_disabled.append("9.06");
  yango_section[kDisabled] = std::move(yango_disabled);

  Json::Value yango_fs{Json::objectValue};
  yango_fs["yango_1"] = "8.73";
  yango_fs["yango_2"] = "9.03";
  yango_fs["default_2"] = "9.00";  // overrides up
  yango_section[kFeatureSupport] = std::move(yango_fs);

  // ios
  Json::Value ios_section{Json::objectValue};
  ios_section[kMin] = "1.00";
  ios_section[kCurrent] = "1.00";

  Json::Value ios_disabled{Json::arrayValue};
  ios_disabled.append("1.01");
  ios_section[kDisabled] = std::move(ios_disabled);

  Json::Value ios_fs{Json::objectValue};
  ios_fs["ios_1"] = "0.99";
  ios_fs["ios_2"] = "1.02";
  ios_fs["default_2"] = "1.00";
  ios_section[kFeatureSupport] = std::move(ios_fs);

  // compose and return
  Json::Value version_settings{Json::objectValue};
  version_settings["__default__"] = std::move(default_section);
  version_settings["taximeter"] = std::move(production_section);
  version_settings["taximeter-yango"] = std::move(yango_section);
  version_settings["taximeter-ios"] = std::move(ios_section);
  return version_settings;
}()};

config::DocsMap DocsMapForTestLocal() {
  const std::string path{CONFIG_FALLBACK_DIR "/configs.json"};
  auto fallback_values = models::configs::ReadFallback(path);
  fallback_values[kConfigName] = taximeter_version_by_build;
  return models::configs::JsonToDocsMap(fallback_values);
}

}  // namespace

TEST(TestTaximeterVersionSettingsByBuild, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& cfg = config.Get<config::VersionSettingsByBuild>();
  const App app{};
  ASSERT_EQ("8.78", cfg.GetMin(app).ToString(true));
  EXPECT_THROW(cfg.GetCurrent(app), std::runtime_error);
}

TEST(TestTaximeterVersionSettingsByBuild, MinVersion) {
  const auto& docs_map = DocsMapForTestLocal();
  const auto& config = config::Config(docs_map);
  const auto& cfg = config.Get<config::VersionSettingsByBuild>();

  ASSERT_EQ("8.80",
            cfg.GetMin(Type::Production, Platform::kAndroid).ToString(true));
  ASSERT_TRUE(cfg.IsVersionSupported({Type::Production, "8.80"}));
  ASSERT_FALSE(cfg.IsVersionSupported({Type::Production, "8.79"}));

  ASSERT_EQ("8.78",
            cfg.GetMin(Type::Azerbaijan, Platform::kAndroid).ToString(true));
  ASSERT_TRUE(cfg.IsVersionSupported({Type::Azerbaijan, "8.78"}));
  ASSERT_FALSE(cfg.IsVersionSupported({Type::Azerbaijan, "8.77"}));

  ASSERT_EQ("8.78", cfg.GetMin(Type::Beta, Platform::kAndroid).ToString(true));
  ASSERT_TRUE(cfg.IsVersionSupported({Type::Beta, "8.78"}));
  ASSERT_FALSE(cfg.IsVersionSupported({Type::Beta, "8.77"}));

  ASSERT_EQ("8.95", cfg.GetMin(Type::Yango, Platform::kAndroid).ToString(true));
  ASSERT_TRUE(cfg.IsVersionSupported({Type::Yango, "8.95"}));
  ASSERT_FALSE(cfg.IsVersionSupported({Type::Yango, "8.94"}));

  ASSERT_EQ("1.00", cfg.GetMin(Type::Yango, Platform::kIos).ToString(true));
  ASSERT_TRUE(cfg.IsVersionSupported({Type::Yango, "1.00", Platform::kIos}));
  ASSERT_FALSE(cfg.IsVersionSupported({Type::Yango, "0.99", Platform::kIos}));
}

TEST(TestTaximeterVersionSettingsByBuild, DisabledVersions) {
  const auto& docs_map = DocsMapForTestLocal();
  const auto& config = config::Config(docs_map);
  const auto& cfg = config.Get<config::VersionSettingsByBuild>();

  // 8.98 disabled for all
  for (std::uint32_t type = 1; type <= 12; ++type) {
    const App app{Type(type), "8.98"};

    ASSERT_TRUE(cfg.IsVersionDisabled(app));
    ASSERT_FALSE(cfg.IsVersionSupported(app));
  }

  // 8.98 disabled for all (with build)
  for (std::uint32_t type = 1; type <= 12; ++type) {
    const App app{Type(type), "8.98 (1234)"};

    ASSERT_TRUE(cfg.IsVersionDisabled(app));
    ASSERT_FALSE(cfg.IsVersionSupported(app));
  }

  // 9.02 disabled only for Production
  ASSERT_FALSE(cfg.IsVersionSupported({Type::Production, "9.02"}));
  ASSERT_FALSE(cfg.IsVersionSupported({Type::Production, "9.02 (1234)"}));
  ASSERT_FALSE(cfg.IsVersionSupported({Type::Production, "9.2"}));
  ASSERT_FALSE(cfg.IsVersionSupported({Type::Production, "9.2 (1234)"}));
  ASSERT_TRUE(cfg.IsVersionDisabled({Type::Production, "9.02"}));
  ASSERT_TRUE(cfg.IsVersionDisabled({Type::Production, "9.02 (1234)"}));
  ASSERT_TRUE(cfg.IsVersionDisabled({Type::Production, "9.2"}));
  ASSERT_TRUE(cfg.IsVersionDisabled({Type::Production, "9.2 (1234)"}));
  ASSERT_TRUE(cfg.IsVersionSupported({Type::Azerbaijan, "9.02"}));
  ASSERT_TRUE(cfg.IsVersionSupported({Type::Experimental, "9.02"}));
  ASSERT_TRUE(cfg.IsVersionSupported({Type::Beta, "9.02", Platform::kIos}));

  // 9.06 disabled only for Yango
  ASSERT_FALSE(cfg.IsVersionSupported({Type::Yango, "9.06"}));
  ASSERT_TRUE(cfg.IsVersionSupported({Type::Beta, "9.06"}));
  ASSERT_TRUE(cfg.IsVersionSupported({Type::Production, "9.06"}));
  ASSERT_TRUE(cfg.IsVersionSupported({Type::Uber, "9.06"}));
  ASSERT_TRUE(
      cfg.IsVersionSupported({Type::Azerbaijan, "9.06", Platform::kIos}));
}

TEST(TestTaximeterVersionSettingsByBuild, FeatureSupport) {
  const auto& docs_map = DocsMapForTestLocal();
  const auto& config = config::Config(docs_map);
  const auto& cfg = config.Get<config::VersionSettingsByBuild>();

  // default_1 supported for all (old feature)
  // default_3 unsupported for all - too new, absent in config
  for (std::uint32_t type = 1; type <= 12; ++type) {
    const App app{Type(type), "8.98"};

    ASSERT_TRUE(cfg.IsFeatureSupported("default_1", app));
    ASSERT_FALSE(cfg.IsFeatureSupported("default_3", app));
  }

  // default_2 overrides
  ASSERT_TRUE(cfg.IsFeatureSupported("default_2", {Type::Production, "8.90"}));
  ASSERT_FALSE(cfg.IsFeatureSupported("default_2", {Type::Production, "8.89"}));
  ASSERT_TRUE(cfg.IsFeatureSupported("default_2", {Type::Uber, "8.95"}));
  ASSERT_FALSE(cfg.IsFeatureSupported("default_2", {Type::Azerbaijan, "8.94"}));
  ASSERT_TRUE(
      cfg.IsFeatureSupported("default_2", {Type::Experimental, "8.95"}));
  ASSERT_FALSE(
      cfg.IsFeatureSupported("default_2", {Type::Experimental, "8.94"}));
  ASSERT_TRUE(cfg.IsFeatureSupported("default_2", {Type::Yango, "9.00"}));
  ASSERT_FALSE(cfg.IsFeatureSupported("default_2", {Type::Yango, "8.99"}));
  ASSERT_TRUE(cfg.IsFeatureSupported(
      "default_2", {Type::Production, "1.00", Platform::kIos}));
  ASSERT_FALSE(cfg.IsFeatureSupported(
      "default_2", {Type::Production, "0.99", Platform::kIos}));

  // zero in version string
  ASSERT_TRUE(cfg.IsFeatureSupported("yango_2", {Type::Yango, "9.03"}));
  ASSERT_TRUE(cfg.IsFeatureSupported("yango_2", {Type::Yango, "9.03 (1234)"}));
  ASSERT_TRUE(cfg.IsFeatureSupported("yango_2", {Type::Yango, "9.3"}));
  ASSERT_TRUE(cfg.IsFeatureSupported("yango_2", {Type::Yango, "9.3 (5678)"}));

  // dont consider other builds
  ASSERT_FALSE(cfg.IsFeatureSupported("production_1", {Type::Yango, "99.99"}));
  ASSERT_FALSE(cfg.IsFeatureSupported("production_1", {Type::Uber, "99.99"}));
  ASSERT_FALSE(
      cfg.IsFeatureSupported("production_1", {Type::Experimental, "99.99"}));
  ASSERT_FALSE(cfg.IsFeatureSupported("yango_1", {Type::Production, "99.99"}));
  ASSERT_FALSE(cfg.IsFeatureSupported("yango_1", {Type::Azerbaijan, "99.99"}));
  ASSERT_FALSE(cfg.IsFeatureSupported("yango_1", {Type::Sdc, "99.99"}));

  ASSERT_EQ("8.95", cfg.GetMinVersionForFeature("default_2")->ToString());
  ASSERT_FALSE(cfg.GetMinVersionForFeature("unsupported"));
}
