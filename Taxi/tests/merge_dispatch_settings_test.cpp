#include "common.hpp"

#include <gtest/gtest.h>

#include <dispatch-settings/caches/dispatch_settings_cache.hpp>
#include <dispatch-settings/details/config.hpp>
#include <dispatch-settings/details/service_dispatch_settings.hpp>
#include <dispatch-settings/models/index.hpp>
#include <dispatch-settings/models/settings_values_serialization.hpp>
#include <dispatch-settings/resolvers/json_map_experiments.hpp>

#include <testing/taxi_config.hpp>
#include <userver/dynamic_config/fwd.hpp>
#include <userver/dynamic_config/value.hpp>
#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value_builder.hpp>
#include <userver/fs/blocking/read.hpp>
#include <userver/utils/shared_readable_ptr.hpp>

#include <cstddef>
#include <unordered_set>

namespace dispatch_settings::test {

namespace {
const CommonSettings kCommonSettings;
const std::vector<std::string> kDefaultTariffTags{"a", "c"};
const std::vector<std::string> kExistingTariffTags{"b", "c", "d"};
const std::vector<std::string> kMergedTags{"a", "c", "b", "d"};
const std::optional<uint32_t> kDefaultTariffComboPreferred = 5;
const std::optional<uint32_t> kExistingTariffComboPreferred = std::nullopt;
}  // namespace

std::shared_ptr<const dispatch_settings::models::Index>
CreateServiceDataForMerge() {
  dispatch_settings::models::Index index;

  const auto default_tariff_script_bonus_params =
      ReadStatic("script_bonus_params_to_merge1.json");
  formats::json::ValueBuilder builder_default_tariff =
      CreateSearchSettingsClassesValues(10);
  builder_default_tariff["SCRIPT_BONUS_PARAMS"] =
      formats::json::FromString(default_tariff_script_bonus_params);
  builder_default_tariff["DISPATCH_DRIVER_TAGS_BLOCK"] = kDefaultTariffTags;
  builder_default_tariff["COMBO_PREFERRED"] = kDefaultTariffComboPreferred;
  index.settings.emplace(
      dispatch_settings::models::SettingsKey{kCommonSettings.def,
                                             kCommonSettings.def},
      builder_default_tariff.ExtractValue()
          .As<dispatch_settings::models::SettingsValues>());

  const auto existing_tariff_script_bonus_params =
      ReadStatic("script_bonus_params_to_merge2.json");

  formats::json::ValueBuilder builder_existing_tariff =
      CreateSearchSettingsClassesValues(11);
  builder_existing_tariff["SCRIPT_BONUS_PARAMS"] =
      formats::json::FromString(existing_tariff_script_bonus_params);
  builder_existing_tariff["DISPATCH_DRIVER_TAGS_BLOCK"] = kExistingTariffTags;
  builder_existing_tariff["COMBO_PREFERRED"] = kExistingTariffComboPreferred;
  index.settings.emplace(
      dispatch_settings::models::SettingsKey{kCommonSettings.def,
                                             kCommonSettings.test_tariff},
      builder_existing_tariff.ExtractValue()
          .As<dispatch_settings::models::SettingsValues>());

  return std::make_shared<const dispatch_settings::models::Index>(index);
}

TEST(MergeDispatchSettings, MergeSettingsServiceTest) {
  const auto config = CreateConfig();
  auto data = CreateServiceDataForMerge();

  dispatch_settings::details::ServiceDispatchSettings service_settings(
      [&data]() { return data; }, config.GetSource());
  dispatch_settings::DispatchSettings::FetchParams params(
      kCommonSettings.def, {kCommonSettings.def, kCommonSettings.test_tariff});

  const auto script_bonus_params_merged =
      ReadStatic("script_bonus_params_merged.json");
  const auto script_bonus_params_etalon =
      formats::json::FromString(script_bonus_params_merged);

  auto settings = service_settings.FetchPrepared(params);
  ASSERT_TRUE(settings.script_bonus_params.has_value());
  ASSERT_EQ(*settings.script_bonus_params, script_bonus_params_etalon);
  ASSERT_EQ(settings.dispatch_driver_tags_block, kMergedTags);

  ASSERT_NE(settings.combo_preferred, kDefaultTariffComboPreferred);
  ASSERT_EQ(settings.combo_preferred, kExistingTariffComboPreferred);
}

}  // namespace dispatch_settings::test
