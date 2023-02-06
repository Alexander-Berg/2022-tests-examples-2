#pragma once

#include <userver/dynamic_config/storage_mock.hpp>
#include <userver/formats/json/value.hpp>
#include <userver/formats/json/value_builder.hpp>

#include <dispatch-settings/models/settings_values.hpp>
#include <testing/taxi_config.hpp>

namespace dispatch_settings::test {

struct CommonSettings {
  CommonSettings();

  const std::string non_existing_zone = "nonexisting_zone";
  const std::string non_existing_tariff = "nonexisting_tariff";
  const std::string non_existing_tariff_with_group =
      "nonexisting_tariff_with_group";
  const std::string non_existing_group = "nonexisting_group";
  const std::string test_zone = "test_zone";
  const std::string test_tariff = "test_tariff";
  const std::string test_tariff2 = "test_tariff2";
  const std::string test_tariff3 = "test_tariff3";
  const std::string group1 = "group1";
  const std::string group2 = "group2";
  const std::string group_with_partial_overrided_fallback =
      "group_with_partial_overrided_fallback";
  const std::string default_group1 = "__default__group1__";
  const std::string default_group2 = "__default__group2__";
  const std::string default_group_with_partial_overrided_fallback =
      "__default__group_with_partial_overrided_fallback";
  const std::string default_non_existing_group =
      "__default__non_existing_group";
  const std::string test_tag = "test_tag";
  const std::string def = "__default__";
  const int level_multi = 1024;
  const int fallback_config_default_level = 1;
  const int fallback_config_non_existing_group_level = 2;
  const std::string script_bonus_params_json =
      "{\"PARAM_1\": 1, \"PARAM_2\": \"abc\"}";
};

std::string ReadStatic(const std::string& name);

formats::json::Value CreateDefaultDict(int val);

formats::json::Value BuildTagsIntMapJson(int val);

formats::json::Value CreateSearchSettingsClassesValues(int val = 0);
formats::json::Value CreateOrderChainSettingsValues(int val = 0);
formats::json::Value CreateSearchSettingsQueryLimitClassesValues(int val = 0);

formats::json::Value CreateMergedValues(int val = 0);
dispatch_settings::models::SettingsValues MakeSettings(int key);

formats::json::Value CreateExperimentsConfig(std::vector<std::string> exps);

formats::json::Value DumpSettingsConfig();
formats::json::Value SupplyRadiusConfig();

dynamic_config::StorageMock CreateConfig(
    std::vector<std::string> experiments = {});

}  // namespace dispatch_settings::test
