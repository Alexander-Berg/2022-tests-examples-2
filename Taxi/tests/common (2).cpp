#include "common.hpp"

#include <testing/source_path.hpp>
#include <userver/formats/json/serialize.hpp>
#include <userver/fs/blocking/read.hpp>

#include <taxi_config/dispatch-settings/taxi_config.hpp>

#include <dispatch-settings/details/config.hpp>
#include <dispatch-settings/models/settings_values_serialization.hpp>

namespace dispatch_settings::test {

namespace {

const CommonSettings kCommonSettings;
const std::string def = kCommonSettings.def;

struct FromJson final {
  formats::json::Value value;

  template <typename T>
  operator T() const {
    return value.As<T>();
  }
};

void UpMerge(formats::json::ValueBuilder& out, formats::json::Value val,
             const std::string& prefix) {
  for (auto it = val.begin(), end = val.end(); it != end; ++it) {
    out[prefix + it.GetName()] = *it;
  }
}

}  // namespace

CommonSettings::CommonSettings() {}

std::string ReadStatic(const std::string& name) {
  return fs::blocking::ReadFileContents(
      utils::CurrentSourcePath("tests/static/" + name));
}

formats::json::Value CreateDefaultDict(int val) {
  formats::json::ValueBuilder builder;

  builder[def] = val;

  return builder.ExtractValue();
}

formats::json::Value BuildTagsIntMapJson(int val) {
  formats::json::ValueBuilder builder;

  builder["sample_tag"] = val;

  return builder.ExtractValue();
}

formats::json::Value CreateSearchSettingsClassesValues(int val) {
  formats::json::ValueBuilder builder;
  const int key = kCommonSettings.level_multi * val;

  builder["ANTISURGE_BONUS_COEF"] = key + 4;
  builder["ANTISURGE_BONUS_GAP"] = key + 5;
  builder["DISPATCH_DRIVER_TAGS_BLOCK"] =
      std::vector<std::string>{kCommonSettings.test_tag};
  builder["DISPATCH_DRIVER_TAGS_BONUSES"] = CreateDefaultDict(key + 6);
  builder["DISPATCH_MAX_TARIFF_BONUS_SECONDS"] = CreateDefaultDict(key + 8);
  builder["MAX_ROBOT_DISTANCE"] = key + 14;
  builder["MAX_ROBOT_TIME"] = key + 15;
  builder["MIN_URGENCY"] = key + 16;
  builder["SURGE_BONUS_COEF"] = key + 20;
  builder["WAVE_THICKNESS_MINUTES"] = key + 21;

  builder["DISPATCH_MAX_POSITIVE_BONUS_SECONDS"] = key + 23;
  builder["DISPATCH_MIN_NEGATIVE_BONUS_SECONDS"] = key + 24;
  builder["SURGES_RATIO_MIN_BONUS"] = key + 25;
  builder["SURGES_RATIO_MAX_BONUS"] = key + 26;
  builder["SURGES_RATIO_BONUS_COEFF"] = key + 27;
  builder["SCRIPT_BONUS_PARAMS"] =
      formats::json::FromString(kCommonSettings.script_bonus_params_json);
  builder["TAGS_PREFERRED"] = BuildTagsIntMapJson(key + 37);
  builder["NO_TAGS_PREFERRED"] = BuildTagsIntMapJson(key + 38);
  builder["NO_REPOSITION_PREFERRED"] = key + 39;
  builder["CHAIN_PREFERRED"] = key + 46;
  builder["SAME_PARK_PREFERRED"] = key + 47;
  builder["PREFERRED_PRIORITY"] = std::vector<std::string>{
      "chain", "busy", "no_reposition", "no_tags", "tags", "same_park"};

  builder["QUERY_LIMIT_FREE_PREFERRED"] = key + 34;
  builder["QUERY_LIMIT_LIMIT"] = key + 35;
  builder["QUERY_LIMIT_FREE_PREFERRED_ETA"] = key + 51;
  builder["QUERY_LIMIT_LIMIT_ETA"] = key + 52;

  builder["PEDESTRIAN_DISABLED"] = false;
  builder["PEDESTRIAN_ONLY"] = true;
  builder["PEDESTRIAN_MAX_SEARCH_RADIUS"] = key + 40;
  builder["PEDESTRIAN_MAX_SEARCH_ROUTE_DISTANCE"] = key + 41;
  builder["PEDESTRIAN_MAX_SEARCH_ROUTE_TIME"] = key + 42;
  builder["PEDESTRIAN_MAX_ORDER_ROUTE_DISTANCE"] = key + 43;
  builder["PEDESTRIAN_MAX_ORDER_ROUTE_TIME"] = key + 44;

  {
    formats::json::ValueBuilder p_settings;
    p_settings["MAX_SEARCH_RADIUS"] = key + 40;
    p_settings["MAX_SEARCH_ROUTE_DISTANCE"] = key + 41;
    p_settings["MAX_SEARCH_ROUTE_TIME"] = key + 42;
    p_settings["MAX_ORDER_ROUTE_DISTANCE"] = key + 43;
    p_settings["MAX_ORDER_ROUTE_TIME"] = key + 44;
    builder["PEDESTRIAN_SETTINGS"]["bicycle"] = std::move(p_settings);
  }
  {
    formats::json::ValueBuilder p_settings;
    p_settings["MAX_SEARCH_RADIUS"] = key + 49;
    p_settings["MAX_SEARCH_ROUTE_DISTANCE"] = key + 50;
    p_settings["MAX_SEARCH_ROUTE_TIME"] = key + 51;
    p_settings["MAX_ORDER_ROUTE_DISTANCE"] = key + 52;
    p_settings["MAX_ORDER_ROUTE_TIME"] = key + 53;
    builder["PEDESTRIAN_SETTINGS"]["pedestrian"] = std::move(p_settings);
  }

  builder["SUPPLY_ROUTE_DISTANCE_COEFF"] = key + 45;
  builder["SUPPLY_ROUTE_TIME_COEFF"] = key + 46;
  builder["PAID_SUPPLY_ROUTE_DISTANCE_COEFF"] = key + 47;
  builder["PAID_SUPPLY_ROUTE_TIME_COEFF"] = key + 48;

  builder["PAID_SUPPLY_MAX_SEARCH_ROUTE_DISTANCE"] = key + 55;
  builder["PAID_SUPPLY_MAX_LINE_DIST"] = key + 56;
  builder["PAID_SUPPLY_MAX_SEARCH_ROUTE_TIME"] = key + 57;

  builder["COMBO_PREFERRED"] = key + 58;

  return builder.ExtractValue();
}

formats::json::Value CreateOrderChainSettingsValues(int val) {
  formats::json::ValueBuilder builder;
  const int key = kCommonSettings.level_multi * val;

  // ORDER_CHAIN_SETTINGS
  builder["MAX_LINE_DISTANCE"] = key + 29;
  builder["MAX_ROUTE_DISTANCE"] = key + 30;
  builder["MAX_ROUTE_TIME"] = key + 31;
  builder["MAX_TOTAL_TIME"] = key + 59;
  builder["MAX_TOTAL_DISTANCE"] = key + 60;
  builder["PAX_EXCHANGE_TIME"] = key + 33;

  return builder.ExtractValue();
}

formats::json::Value CreateSearchSettingsQueryLimitClassesValues(int val) {
  formats::json::ValueBuilder builder;
  const int key = kCommonSettings.level_multi * val;

  builder["MAX_LINE_DIST"] = key + 36;

  return builder.ExtractValue();
}

formats::json::Value CreateMergedValues(int val) {
  formats::json::ValueBuilder builder = CreateSearchSettingsClassesValues(val);

  UpMerge(builder, CreateOrderChainSettingsValues(val), "ORDER_CHAIN_");
  UpMerge(builder, CreateSearchSettingsQueryLimitClassesValues(val),
          "QUERY_LIMIT_");

  return builder.ExtractValue();
}

dispatch_settings::models::SettingsValues MakeSettings(int key) {
  return CreateMergedValues(key)
      .As<dispatch_settings::models::SettingsValues>();
}

formats::json::Value CreateExperimentsConfig(std::vector<std::string> exps) {
  formats::json::ValueBuilder builder;
  if (!exps.empty()) {
    formats::json::ValueBuilder experiments(formats::json::Type::kArray);
    for (const auto& exp : exps) {
      experiments.PushBack(exp);
    }
    builder["experiment_names"] = experiments;
  }
  return builder.ExtractValue();
}

formats::json::Value CreateFallbackConfig() {
  formats::json::ValueBuilder fallback_config;
  fallback_config["__default__"] =
      MakeSettings(kCommonSettings.fallback_config_default_level);
  fallback_config[kCommonSettings.non_existing_group] =
      MakeSettings(kCommonSettings.fallback_config_non_existing_group_level);
  fallback_config[kCommonSettings.group_with_partial_overrided_fallback] =
      []() {
        formats::json::ValueBuilder builder;
        builder["MAX_ROBOT_TIME"] = 6666;
        builder["MAX_ROBOT_DISTANCE"] = 6667;
        return builder;
      }();
  return fallback_config.ExtractValue();
}

formats::json::Value DumpSettingsConfig() {
  formats::json::ValueBuilder builder;
  builder["read_enabled"] = true;
  builder["write_enabled"] = true;
  return builder.ExtractValue();
}

dynamic_config::StorageMock CreateConfig(std::vector<std::string> experiments) {
  details::Config old_config;
  old_config.dispatch_settings_fallback_raw = CreateFallbackConfig();

  return dynamic_config::StorageMock{
      {details::kConfigRaw, old_config},
      {taxi_config::DISPATCH_SETTINGS_OVERRIDE_SETTINGS,
       FromJson{CreateExperimentsConfig(experiments)}},
      {taxi_config::DISPATCH_SETTINGS_CACHE_UPDATE_ENABLED, true},
      {taxi_config::DISPATCH_SETTINGS_USERVICES_CACHE_UPDATE_ITERATION_REQUESTS,
       10},
      {taxi_config::DISPATCH_SETTINGS_USERVICES_DUMP_SETTINGS,
       FromJson{DumpSettingsConfig()}},
  };
}

}  // namespace dispatch_settings::test
