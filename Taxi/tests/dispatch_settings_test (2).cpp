#include "common.hpp"

#include <cstddef>
#include <set>
#include <unordered_set>

#include <fmt/format.h>
#include <gtest/gtest.h>

#include <userver/dynamic_config/fwd.hpp>
#include <userver/dynamic_config/storage_mock.hpp>
#include <userver/dynamic_config/value.hpp>
#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value_builder.hpp>
#include <userver/fs/blocking/read.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/algo.hpp>

#include <testing/taxi_config.hpp>

#include <dispatch-settings/caches/dispatch_settings_cache.hpp>
#include <dispatch-settings/details/config.hpp>
#include <dispatch-settings/details/service_dispatch_settings.hpp>
#include <dispatch-settings/models/index.hpp>
#include <dispatch-settings/models/settings_values_serialization.hpp>
#include <dispatch-settings/resolvers/json_map_experiments.hpp>

namespace {

const char* override_value_field_name = "dispatch_settings_override_values";
const std::string exp_1_name = "experiment_1";
const std::string exp_2_name = "experiment_2";

const dispatch_settings::test::CommonSettings kCommonSettings;
const std::string non_z = kCommonSettings.non_existing_zone;
const std::string non_t = kCommonSettings.non_existing_tariff;
const std::string non_t_with_g = kCommonSettings.non_existing_tariff_with_group;
const std::string non_g =
    kCommonSettings.non_existing_group;  // у группы нет настроек
const std::string non_g_def = kCommonSettings.default_non_existing_group;

const std::string exi_z = kCommonSettings.test_zone;
const std::string exi_t = kCommonSettings.test_tariff;
const std::string exi_g = kCommonSettings.group1;
const std::string exi_g_def = kCommonSettings.default_group1;
const std::string def = kCommonSettings.def;

template <typename T>
bool operator!=(const dynamic_config::ValueDict<T>& lhs,
                const dynamic_config::ValueDict<T>& rhs) {
  auto lhs_size = std::distance(lhs.begin(), lhs.end());
  auto rhs_size = std::distance(rhs.begin(), rhs.end());

  if (lhs_size != rhs_size) {
    return true;
  }

  auto check_iterator_with_obj =
      [](const dynamic_config::ValueDict<T>& first,
         const dynamic_config::ValueDict<T>& second) {
        auto iterator = first.begin();
        for (; iterator != first.end(); ++iterator) {
          auto found = second.Get(iterator->first);
          if (found != iterator->second) {
            return true;
          }
        }

        return false;
      };

  if (check_iterator_with_obj(lhs, rhs)) {
    return true;
  }

  if (check_iterator_with_obj(rhs, lhs)) {
    return true;
  }

  return false;
}

template <typename T>
bool operator!=(const interval::Interval<T>& lhs,
                const interval::Interval<T>& rhs) {
  return lhs.Min() != rhs.Min() || lhs.Max() != rhs.Max();
}

bool CompareDouble(double lhs, double rhs) {
  return std::abs(lhs - rhs) <= 0.0001;
}

}  // namespace

namespace dispatch_settings::models {

#define COMPARE_DEFAULT(FIELD_NAME) \
  if (lhs.FIELD_NAME != rhs.FIELD_NAME) return false

#define COMPARE_DOUBLE(FIELD_NAME) \
  if (std::abs(lhs.FIELD_NAME - rhs.FIELD_NAME) > 0.0001) return false

bool operator==(
    const dispatch_settings::models::SettingsValues::PedestrianSettings& lhs,
    const dispatch_settings::models::SettingsValues::PedestrianSettings& rhs) {
  COMPARE_DEFAULT(max_search_radius);
  COMPARE_DEFAULT(max_search_route_distance);
  COMPARE_DEFAULT(max_search_route_time);
  COMPARE_DEFAULT(max_order_route_distance);
  COMPARE_DEFAULT(max_order_route_time);
  return true;
}

bool operator==(const dispatch_settings::models::SettingsValues& lhs,
                const dispatch_settings::models::SettingsValues& rhs) {
  COMPARE_DOUBLE(max_robot_time);
  COMPARE_DOUBLE(max_robot_distance);
  COMPARE_DEFAULT(min_urgency);
  COMPARE_DEFAULT(wave_thickness_minutes);
  COMPARE_DOUBLE(surge_bonus_coef);
  COMPARE_DOUBLE(antisurge_bonus_coef);
  COMPARE_DOUBLE(antisurge_bonus_gap);
  COMPARE_DEFAULT(dispatch_max_tariff_bonus_seconds);
  COMPARE_DEFAULT(dispatch_max_positive_bonus_seconds);
  COMPARE_DEFAULT(dispatch_min_negative_bonus_seconds);
  COMPARE_DEFAULT(dispatch_driver_tags_bonuses);
  COMPARE_DEFAULT(dispatch_driver_tags_block);
  COMPARE_DEFAULT(surges_ratio_bonus);
  COMPARE_DOUBLE(surges_ratio_bonus_coeff);
  COMPARE_DEFAULT(order_chain_max_line_distance);
  COMPARE_DEFAULT(order_chain_max_route_distance);
  COMPARE_DEFAULT(order_chain_max_route_time);
  COMPARE_DEFAULT(order_chain_max_total_time);
  COMPARE_DEFAULT(order_chain_max_total_distance);
  COMPARE_DEFAULT(order_chain_pax_exchange_time);
  COMPARE_DEFAULT(query_limit_free_preferred);
  COMPARE_DEFAULT(query_limit_limit);
  COMPARE_DEFAULT(query_limit_max_line_dist);
  COMPARE_DEFAULT(script_bonus_params);
  COMPARE_DEFAULT(tags_preferred);
  COMPARE_DEFAULT(no_tags_preferred);
  COMPARE_DEFAULT(no_reposition_preferred);
  COMPARE_DEFAULT(query_limit_free_preferred_eta);
  COMPARE_DEFAULT(query_limit_limit_eta);
  COMPARE_DEFAULT(pedestrian_disabled);
  COMPARE_DEFAULT(pedestrian_only);
  COMPARE_DEFAULT(pedestrian_max_search_radius);
  COMPARE_DEFAULT(pedestrian_max_search_route_distance);
  COMPARE_DEFAULT(pedestrian_max_search_route_time);
  COMPARE_DEFAULT(pedestrian_max_order_route_distance);
  COMPARE_DEFAULT(pedestrian_max_order_route_time);
  COMPARE_DEFAULT(pedestrian_settings);
  COMPARE_DEFAULT(paid_supply_max_search_route_distance);
  COMPARE_DEFAULT(paid_supply_max_line_distance);
  COMPARE_DEFAULT(paid_supply_max_search_route_time);
  COMPARE_DEFAULT(combo_preferred);

  return true;
}

#undef COMPARE_DEFAULT
#undef COMPARE_DOUBLE
}  // namespace dispatch_settings::models

namespace dispatch_settings::test {

dynamic_config::ValueDict<int32_t> CreateDefaultValueDict(
    const std::string& name, int val) {
  return dynamic_config::ValueDict<int32_t>(name, {{def, val}});
}

std::unordered_map<std::string, uint32_t> BuildTagsIntMap(int val) {
  return std::unordered_map<std::string, uint32_t>{{"sample_tag", val}};
}

dispatch_settings::models::SettingsValues CreateSettingsValues(int val = 0) {
  const int key = kCommonSettings.level_multi * val;

  dispatch_settings::models::SettingsValues result;

  result.antisurge_bonus_coef = key + 4;
  result.antisurge_bonus_gap = key + 5;
  result.dispatch_driver_tags_block =
      std::vector<std::string>{kCommonSettings.test_tag};
  result.dispatch_driver_tags_bonuses =
      CreateDefaultValueDict("DISPATCH_DRIVER_TAGS_BONUSES", key + 6);
  result.dispatch_max_tariff_bonus_seconds =
      CreateDefaultValueDict("DISPATCH_MAX_TARIFF_BONUS_SECONDS", key + 8);
  result.max_robot_distance = key + 14;
  result.max_robot_time = key + 15;
  result.min_urgency = key + 16;
  result.surge_bonus_coef = key + 20;
  result.wave_thickness_minutes = key + 21;

  result.dispatch_max_positive_bonus_seconds = key + 23;
  result.dispatch_min_negative_bonus_seconds = key + 24;
  result.surges_ratio_bonus = {key + 25, key + 26};
  result.surges_ratio_bonus_coeff = key + 27;

  result.order_chain_max_line_distance = key + 29;
  result.order_chain_max_route_distance = key + 30;
  result.order_chain_max_route_time = key + 31;
  result.order_chain_max_total_time = key + 59;
  result.order_chain_max_total_distance = key + 60;
  result.order_chain_pax_exchange_time = key + 33;

  result.query_limit_free_preferred = key + 34;
  result.query_limit_limit = key + 35;
  result.query_limit_max_line_dist = key + 36;

  result.script_bonus_params =
      formats::json::FromString(kCommonSettings.script_bonus_params_json);

  result.tags_preferred = BuildTagsIntMap(key + 37);
  result.no_tags_preferred = BuildTagsIntMap(key + 38);
  result.no_reposition_preferred = key + 39;
  result.chain_preferred = key + 46;
  result.same_park_preferred = key + 47;
  result.preferred_priority = {
      dispatch_settings::models::SearchPreferenceType::Chain,
      dispatch_settings::models::SearchPreferenceType::Busy,
      dispatch_settings::models::SearchPreferenceType::NoReposition,
      dispatch_settings::models::SearchPreferenceType::NoTags,
      dispatch_settings::models::SearchPreferenceType::Tags,
      dispatch_settings::models::SearchPreferenceType::SamePark,
  };

  result.query_limit_free_preferred_eta = key + 51;
  result.query_limit_limit_eta = key + 52;

  result.pedestrian_disabled = false;
  result.pedestrian_only = true;
  result.pedestrian_max_search_radius = key + 40;
  result.pedestrian_max_search_route_distance = key + 41;
  result.pedestrian_max_search_route_time = std::chrono::seconds(key + 42);
  result.pedestrian_max_order_route_distance = key + 43;
  result.pedestrian_max_order_route_time = std::chrono::seconds(key + 44);

  result.pedestrian_settings = {"",
                                {{"bicycle",
                                  {
                                      static_cast<uint32_t>(key + 40),  //
                                      key + 41,                         //
                                      std::chrono::seconds(key + 42),   //
                                      static_cast<uint32_t>(key + 43),  //
                                      std::chrono::seconds(key + 44)    //
                                  }},
                                 {"pedestrian",
                                  {
                                      static_cast<uint32_t>(key + 49),  //
                                      key + 50,                         //
                                      std::chrono::seconds(key + 51),   //
                                      static_cast<uint32_t>(key + 52),  //
                                      std::chrono::seconds(key + 53)    //
                                  }}}};

  result.supply_route_distance_coeff = key + 45;
  result.supply_route_time_coeff = key + 46;
  result.paid_supply_route_distance_coeff = key + 47;
  result.paid_supply_route_time_coeff = key + 48;

  result.paid_supply_max_search_route_distance = key + 55;
  result.paid_supply_max_line_distance = key + 56;
  result.paid_supply_max_search_route_time = key + 57;

  result.combo_preferred = key + 58;

  return result;
}

dispatch_settings::models::Index CreateServiceDataForDump() {
  dispatch_settings::models::Index index;

  index.settings.emplace(dispatch_settings::models::SettingsKey{def, def},
                         MakeSettings(10));
  index.settings.emplace(dispatch_settings::models::SettingsKey{def, exi_t},
                         MakeSettings(11));

  using Tariff = dispatch_settings::models::Tariff;
  using Group = dispatch_settings::models::Group;
  index.tariff_groups = {
      {Tariff(kCommonSettings.default_group1), Group(kCommonSettings.group1)},
      {Tariff(kCommonSettings.default_group2), Group(kCommonSettings.group2)},
      {Tariff(kCommonSettings.test_tariff), Group(kCommonSettings.group1)},
      {Tariff(kCommonSettings.test_tariff2), Group(kCommonSettings.group2)},
      {Tariff(kCommonSettings.test_tariff3), Group(kCommonSettings.group2)},
  };

  return index;
}

std::shared_ptr<const dispatch_settings::models::Index> CreateServiceData() {
  dispatch_settings::models::Index index;

  index.settings.emplace(dispatch_settings::models::SettingsKey{def, def},
                         MakeSettings(10));
  index.settings.emplace(dispatch_settings::models::SettingsKey{def, exi_t},
                         MakeSettings(11));
  index.settings.emplace(dispatch_settings::models::SettingsKey{exi_z, def},
                         MakeSettings(12));
  index.settings.emplace(dispatch_settings::models::SettingsKey{exi_z, exi_t},
                         MakeSettings(13));

  index.settings.emplace(dispatch_settings::models::SettingsKey{def, exi_g_def},
                         MakeSettings(20));
  index.settings.emplace(
      dispatch_settings::models::SettingsKey{exi_z, exi_g_def},
      MakeSettings(21));

  using Tariff = dispatch_settings::models::Tariff;
  using Group = dispatch_settings::models::Group;
  index.tariff_groups = {
      {Tariff(exi_g_def), Group(exi_g)},
      {Tariff{exi_t}, Group{exi_g}},
      {Tariff(non_t_with_g), Group(exi_g)},
  };

  return std::make_shared<const dispatch_settings::models::Index>(index);
}

void ValidateForParameter(
    const dispatch_settings::models::SettingsValues& vals, int param,
    bool validate_merge,
    const std::unordered_set<std::string>& skip_fields_offsets = {}) {
  const int add = param * kCommonSettings.level_multi;

#define ALLOWED(FIELD) \
  (skip_fields_offsets.find(#FIELD) == skip_fields_offsets.end())

  if (ALLOWED(antisurge_bonus_coef)) {
    ASSERT_DOUBLE_EQ(vals.antisurge_bonus_coef, add + 4);
  }
  if (ALLOWED(antisurge_bonus_gap)) {
    ASSERT_DOUBLE_EQ(vals.antisurge_bonus_gap, add + 5);
  }
  if (ALLOWED(max_robot_distance)) {
    ASSERT_DOUBLE_EQ(vals.max_robot_distance, add + 14);
  }
  if (ALLOWED(max_robot_time)) {
    ASSERT_DOUBLE_EQ(vals.max_robot_time, add + 15);
  }
  if (ALLOWED(min_urgency)) {
    ASSERT_EQ(vals.min_urgency, add + 16);
  }
  if (ALLOWED(surge_bonus_coef)) {
    ASSERT_DOUBLE_EQ(vals.surge_bonus_coef, add + 20);
  }
  if (ALLOWED(wave_thickness_minutes)) {
    ASSERT_EQ(vals.wave_thickness_minutes, add + 21);
  }
  if (ALLOWED(dispatch_max_positive_bonus_seconds)) {
    ASSERT_EQ(vals.dispatch_max_positive_bonus_seconds, add + 23);
  }
  if (ALLOWED(dispatch_min_negative_bonus_seconds)) {
    ASSERT_EQ(vals.dispatch_min_negative_bonus_seconds, add + 24);
  }
  if (ALLOWED(surges_ratio_bonus)) {
    ASSERT_EQ(vals.surges_ratio_bonus.Min(), add + 25);
    ASSERT_EQ(vals.surges_ratio_bonus.Max(), add + 26);
  }
  if (ALLOWED(surges_ratio_bonus_coeff)) {
    ASSERT_DOUBLE_EQ(vals.surges_ratio_bonus_coeff, add + 27);
  }

  if (validate_merge) {
    if (ALLOWED(order_chain_max_line_distance)) {
      ASSERT_EQ(vals.order_chain_max_line_distance, add + 29);
    }
    if (ALLOWED(order_chain_max_route_distance)) {
      ASSERT_EQ(vals.order_chain_max_route_distance, add + 30);
    }
    if (ALLOWED(order_chain_max_route_time)) {
      ASSERT_EQ(vals.order_chain_max_route_time, add + 31);
    }
    if (ALLOWED(order_chain_max_total_time)) {
      ASSERT_EQ(*vals.order_chain_max_total_time, add + 59);
    }
    if (ALLOWED(order_chain_max_total_distance)) {
      ASSERT_EQ(*vals.order_chain_max_total_distance, add + 60);
    }
    if (ALLOWED(order_chain_pax_exchange_time)) {
      ASSERT_EQ(vals.order_chain_pax_exchange_time, add + 33);
    }
    if (ALLOWED(query_limit_free_preferred)) {
      ASSERT_EQ(vals.query_limit_free_preferred, add + 34);
    }
    if (ALLOWED(query_limit_limit)) {
      ASSERT_EQ(vals.query_limit_limit, add + 35);
    }
    if (ALLOWED(query_limit_max_line_dist)) {
      ASSERT_EQ(vals.query_limit_max_line_dist, add + 36);
    }
  }

  if (ALLOWED(dispatch_driver_tags_block)) {
    ASSERT_EQ(vals.dispatch_driver_tags_block,
              std::vector<std::string>{kCommonSettings.test_tag});
  }
  if (ALLOWED(dispatch_driver_tags_bonuses)) {
    ASSERT_DOUBLE_EQ(vals.dispatch_driver_tags_bonuses[def], add + 6);
  }
  if (ALLOWED(dispatch_max_tariff_bonus_seconds)) {
    ASSERT_EQ(vals.dispatch_max_tariff_bonus_seconds[def], add + 8);
  }

  if (ALLOWED(script_bonus_params)) {
    ASSERT_EQ(
        vals.script_bonus_params,
        formats::json::FromString(kCommonSettings.script_bonus_params_json));
  }

  if (ALLOWED(tags_preferred)) {
    ASSERT_EQ(vals.tags_preferred, BuildTagsIntMap(add + 37));
  }

  if (ALLOWED(no_tags_preferred)) {
    ASSERT_EQ(vals.no_tags_preferred, BuildTagsIntMap(add + 38));
  }

  if (ALLOWED(no_reposition_preferred)) {
    ASSERT_EQ(vals.no_reposition_preferred, add + 39);
  }

  if (ALLOWED(chain_preferred)) {
    ASSERT_EQ(vals.chain_preferred, add + 46);
  }

  if (ALLOWED(same_park_preferred)) {
    ASSERT_EQ(vals.same_park_preferred, add + 47);
  }

  if (ALLOWED(combo_preferred)) {
    ASSERT_EQ(vals.combo_preferred, add + 58);
  }

  if (ALLOWED(preferred_priority)) {
    std::vector<dispatch_settings::models::SearchPreferenceType> expected{
        dispatch_settings::models::SearchPreferenceType::Chain,
        dispatch_settings::models::SearchPreferenceType::Busy,
        dispatch_settings::models::SearchPreferenceType::NoReposition,
        dispatch_settings::models::SearchPreferenceType::NoTags,
        dispatch_settings::models::SearchPreferenceType::Tags,
        dispatch_settings::models::SearchPreferenceType::SamePark};
    ASSERT_EQ(vals.preferred_priority, expected);
  }

  if (ALLOWED(pedestrian_disabled)) {
    ASSERT_EQ(vals.pedestrian_disabled, false);
  }

  if (ALLOWED(pedestrian_only)) {
    ASSERT_EQ(vals.pedestrian_only, true);
  }

  if (ALLOWED(pedestrian_max_search_radius)) {
    ASSERT_EQ(vals.pedestrian_max_search_radius, add + 40);
  }

  if (ALLOWED(pedestrian_max_search_route_distance)) {
    ASSERT_EQ(*vals.pedestrian_max_search_route_distance, add + 41);
  }

  if (ALLOWED(pedestrian_max_search_route_time)) {
    ASSERT_EQ(*vals.pedestrian_max_search_route_time,
              std::chrono::seconds(add + 42));
  }

  if (ALLOWED(pedestrian_max_order_route_distance)) {
    ASSERT_EQ(vals.pedestrian_max_order_route_distance, add + 43);
  }

  if (ALLOWED(pedestrian_max_order_route_time)) {
    ASSERT_EQ(vals.pedestrian_max_order_route_time,
              std::chrono::seconds(add + 44));
  }

  if (ALLOWED(pedestrian_settings)) {
    dynamic_config::ValueDict<models::SettingsValues::PedestrianSettings>
        true_value{"",
                   {{"bicycle",
                     models::SettingsValues::PedestrianSettings{
                         static_cast<uint32_t>(add + 40),  //
                         static_cast<uint32_t>(add + 41),  //
                         std::chrono::seconds(add + 42),   //
                         static_cast<uint32_t>(add + 43),  //
                         std::chrono::seconds(add + 44)    //
                     }},
                    {"pedestrian", models::SettingsValues::PedestrianSettings{
                                       static_cast<uint32_t>(add + 49),  //
                                       static_cast<uint32_t>(add + 50),  //
                                       std::chrono::seconds(add + 51),   //
                                       static_cast<uint32_t>(add + 52),  //
                                       std::chrono::seconds(add + 53)    //
                                   }}}};

    ASSERT_EQ(vals.pedestrian_settings, true_value);
  }

  if (ALLOWED(supply_route_distance_coeff)) {
    ASSERT_EQ(vals.supply_route_distance_coeff, add + 45);
  }

  if (ALLOWED(supply_route_time_coeff)) {
    ASSERT_EQ(vals.supply_route_time_coeff, add + 46);
  }

  if (ALLOWED(paid_supply_route_distance_coeff)) {
    ASSERT_EQ(vals.paid_supply_route_distance_coeff, add + 47);
  }

  if (ALLOWED(paid_supply_route_time_coeff)) {
    ASSERT_EQ(vals.paid_supply_route_time_coeff, add + 48);
  }
#undef ALLOWED
}

formats::json::Value CreateValueExperimentsJsonFor(
    const std::string& exp_name, int key,
    const std::vector<std::string>& parameters) {
  auto vals = CreateMergedValues(key);

  formats::json::ValueBuilder valueDict;

  for (const auto& param_name : parameters) {
    if (!vals.HasMember(param_name)) {
      throw std::runtime_error(fmt::format(
          "Can't create value experiment. No parameter {}", param_name));
    }

    valueDict[param_name] = vals[param_name];
  }

  formats::json::ValueBuilder result;
  result[override_value_field_name] = valueDict;

  formats::json::ValueBuilder experiments_container;
  experiments_container[exp_name] = result.ExtractValue();
  return experiments_container.ExtractValue();
}

TEST(DispatchSettings, ServiceHappyPath) {
  const auto config = CreateConfig();
  auto data = CreateServiceData();

  dispatch_settings::details::ServiceDispatchSettings settings(
      [&data]() { return data; }, config.GetSource());
  {
    auto non_non_common =
        dispatch_settings::DispatchSettings::FetchDeps(non_z, non_t);
    auto ex_non_common =
        dispatch_settings::DispatchSettings::FetchDeps(exi_z, non_t);
    auto non_ex_common =
        dispatch_settings::DispatchSettings::FetchDeps(non_z, exi_t);
    auto ex_ex_common =
        dispatch_settings::DispatchSettings::FetchDeps(exi_z, exi_t);

    ValidateForParameter(settings.Fetch(non_non_common),
                         kCommonSettings.fallback_config_default_level, true);
    ValidateForParameter(settings.Fetch(ex_non_common),
                         kCommonSettings.fallback_config_default_level, true);
    ValidateForParameter(settings.Fetch(non_ex_common), 11, true);
    ValidateForParameter(settings.Fetch(ex_ex_common), 13, true);
  }
}

TEST(DispatchSettings, FallbackConfigMerge) {
  const auto config = CreateConfig();

  dispatch_settings::models::Index index;

  const auto& group_with_partial_overrided_fallback =
      kCommonSettings.group_with_partial_overrided_fallback;
  const auto& default_group_with_partial_overrided_fallback =
      kCommonSettings.default_group_with_partial_overrided_fallback;

  using Tariff = dispatch_settings::models::Tariff;
  using Group = dispatch_settings::models::Group;
  index.tariff_groups = {
      {Tariff(non_g_def), Group(non_g)},
      {Tariff(non_t_with_g), Group(non_g)},
      {Tariff(exi_t), Group(group_with_partial_overrided_fallback)},
      {Tariff(default_group_with_partial_overrided_fallback),
       Group(group_with_partial_overrided_fallback)},
  };
  const auto data =
      std::make_shared<const dispatch_settings::models::Index>(index);

  dispatch_settings::details::ServiceDispatchSettings settings(
      [&data]() { return data; }, config.GetSource());
  {
    auto non_non =
        dispatch_settings::DispatchSettings::FetchDeps(non_z, non_t_with_g);

    ValidateForParameter(
        settings.Fetch(non_non),
        kCommonSettings.fallback_config_non_existing_group_level, true);
  }
  {
    auto non_non = dispatch_settings::DispatchSettings::FetchDeps(non_z, exi_t);
    const auto partial_override_fallback_settings = settings.Fetch(non_non);
    ValidateForParameter(partial_override_fallback_settings,
                         kCommonSettings.fallback_config_default_level, true,
                         {"max_robot_time", "max_robot_distance"});
    ASSERT_EQ(partial_override_fallback_settings.max_robot_time, 6666);
    ASSERT_EQ(partial_override_fallback_settings.max_robot_distance, 6667);
  }
}

TEST(DispatchSettings, Serialize) {
  auto json = CreateMergedValues(10);
  auto values = CreateSettingsValues(10);

  ASSERT_EQ(formats::json::ValueBuilder(values).ExtractValue(), json);
}

TEST(DispatchSettings, BonusParamsNone) {
  auto values = CreateSettingsValues(10);
  values.script_bonus_params = std::nullopt;

  auto json = formats::json::ValueBuilder(values).ExtractValue();
  ASSERT_TRUE(!json.HasMember("SCRIPT_BONUS_PARAMS"));
}

TEST(DispatchSettings, VisitAllSettings) {
  const auto config = CreateConfig();
  auto data = CreateServiceData();

  dispatch_settings::details::ServiceDispatchSettings settings(
      [&data]() { return data; }, config.GetSource());
  {
    auto non_non_common =
        dispatch_settings::DispatchSettings::FetchDeps(non_z, non_t);
    auto ex_non_common =
        dispatch_settings::DispatchSettings::FetchDeps(exi_z, non_t);
    auto non_ex_common =
        dispatch_settings::DispatchSettings::FetchDeps(non_z, exi_t);
    auto ex_ex_common =
        dispatch_settings::DispatchSettings::FetchDeps(exi_z, exi_t);
  }

  std::set<std::pair<std::string_view, std::string_view>> visited;
  auto markVisited =
      [&visited](
          [[maybe_unused]] const dispatch_settings::models::SettingsValues&
              vals,
          dispatch_settings::DispatchSettings::ZoneNameView zone_name_view,
          dispatch_settings::DispatchSettings::TariffNameView
              tariff_name_view) {
        visited.emplace(zone_name_view.GetUnderlying(),
                        tariff_name_view.GetUnderlying());
        return dispatch_settings::DispatchSettings::IteratingControl::kContinue;
      };

  settings.VisitAllSettings(markVisited);

  ASSERT_EQ(visited.size(), 6);
}

TEST(DispatchSettings, ServiceValueOverride) {
  const auto config = CreateConfig({exp_1_name, exp_2_name});
  auto data = CreateServiceData();

  dispatch_settings::details::ServiceDispatchSettings settings(
      [&data]() { return data; }, config.GetSource());

  auto empty_exps = CreateValueExperimentsJsonFor(exp_1_name, 1000, {});
  auto field_exps =
      CreateValueExperimentsJsonFor(exp_1_name, 1001, {"MAX_ROBOT_TIME"});

  using ExpAdaptor = dispatch_settings::resolvers::JsonMapExperiments;

  {
    auto non_non_common = dispatch_settings::DispatchSettings::FetchDeps(
        non_z, non_t, settings.ResolveExperiments<ExpAdaptor>(empty_exps));
    auto ex_non_common = dispatch_settings::DispatchSettings::FetchDeps(
        exi_z, non_t, settings.ResolveExperiments<ExpAdaptor>(empty_exps));
    auto non_ex_common = dispatch_settings::DispatchSettings::FetchDeps(
        non_z, exi_t, settings.ResolveExperiments<ExpAdaptor>(empty_exps));
    auto ex_ex_common = dispatch_settings::DispatchSettings::FetchDeps(
        exi_z, exi_t, settings.ResolveExperiments<ExpAdaptor>(empty_exps));

    ValidateForParameter(settings.Fetch(non_non_common),
                         kCommonSettings.fallback_config_default_level, true);
    ValidateForParameter(settings.Fetch(ex_non_common),
                         kCommonSettings.fallback_config_default_level, true);
    ValidateForParameter(settings.Fetch(non_ex_common), 11, true);
    ValidateForParameter(settings.Fetch(ex_ex_common), 13, true);
  }

  {
    auto non_non_common = dispatch_settings::DispatchSettings::FetchDeps(
        non_z, non_t, settings.ResolveExperiments<ExpAdaptor>(field_exps));
    auto ex_non_common = dispatch_settings::DispatchSettings::FetchDeps(
        exi_z, non_t, settings.ResolveExperiments<ExpAdaptor>(field_exps));
    auto non_ex_common = dispatch_settings::DispatchSettings::FetchDeps(
        non_z, exi_t, settings.ResolveExperiments<ExpAdaptor>(field_exps));
    auto ex_ex_common = dispatch_settings::DispatchSettings::FetchDeps(
        exi_z, exi_t, settings.ResolveExperiments<ExpAdaptor>(field_exps));

    ValidateForParameter(settings.Fetch(non_non_common),
                         kCommonSettings.fallback_config_default_level, true,
                         {"max_robot_time"});
    ValidateForParameter(settings.Fetch(ex_non_common),
                         kCommonSettings.fallback_config_default_level, true,
                         {"max_robot_time"});
    ValidateForParameter(settings.Fetch(non_ex_common), 11, true,
                         {"max_robot_time"});
    ValidateForParameter(settings.Fetch(ex_ex_common), 13, true,
                         {"max_robot_time"});

    ASSERT_EQ(settings.Fetch(non_non_common).max_robot_time, 1025039);
  }
}

TEST(DispatchSettings, DumpRead) {
  auto index = CreateServiceDataForDump();

  auto string_repr = dispatch_settings::models::Pack(index);

  auto loaded_index = dispatch_settings::models::Unpack(string_repr);

  ASSERT_EQ(index.settings, loaded_index.settings);
}

TEST(DispatchSettings, DumpBackwardCompat) {
  auto index = CreateServiceDataForDump();

  auto dump_v1 = ReadStatic("ds_dump_1.json");

  auto loaded_dump_v1 = dispatch_settings::models::Unpack(dump_v1);

  ASSERT_EQ(index.settings, loaded_dump_v1.settings);

  const auto sorted = [](const auto& unordered) {
    return utils::AsContainer<std::map<dispatch_settings::models::Tariff,
                                       dispatch_settings::models::Group>>(
        unordered);
  };
  ASSERT_EQ(sorted(index.tariff_groups), sorted(loaded_dump_v1.tariff_groups));
}

TEST(DispatchSettings, OrdersLimitServiceTest) {
  const auto config = CreateConfig();
  auto data = CreateServiceData();

  const dispatch_settings::details::ServiceDispatchSettings service_settings(
      [&data]() { return data; }, config.GetSource());
  dispatch_settings::DispatchSettings::FetchParams params(exi_z, {def, exi_t});
  const auto etalon_k1 = kCommonSettings.level_multi * 21;
  const auto etalon_k2 = kCommonSettings.level_multi * 13;

  // paid supply not allowed
  auto settings = service_settings.FetchPrepared(params);
  ASSERT_EQ(settings.query_limit_limit, etalon_k2 + 35);
  ASSERT_EQ(settings.query_limit_free_preferred, etalon_k2 + 34);
  ASSERT_EQ(settings.query_limit_free_preferred_eta, etalon_k2 + 51);
  ASSERT_EQ(settings.query_limit_limit_eta, etalon_k2 + 52);

  ASSERT_EQ(settings.query_limit_max_line_dist, etalon_k2 + 36);
  ASSERT_TRUE(CompareDouble(settings.max_robot_distance,
                            (etalon_k2 + 14) * (etalon_k2 + 45)));
  ASSERT_TRUE(CompareDouble(settings.max_robot_time,
                            (etalon_k2 + 15) * (etalon_k2 + 46)));
  ASSERT_EQ(settings.order_chain_max_line_distance, etalon_k1 + 29);
  ASSERT_EQ(settings.order_chain_max_route_distance, etalon_k1 + 30);
  ASSERT_EQ(settings.order_chain_max_route_time, etalon_k1 + 31);
  ASSERT_EQ(settings.order_chain_max_total_time, etalon_k1 + 59);
  ASSERT_EQ(settings.order_chain_max_total_distance, etalon_k1 + 60);
  ASSERT_EQ(settings.no_reposition_preferred, etalon_k2 + 39);
  ASSERT_EQ(settings.chain_preferred, etalon_k2 + 46);
  ASSERT_EQ(settings.same_park_preferred, etalon_k2 + 47);
  ASSERT_EQ(settings.combo_preferred, etalon_k2 + 58);
  ASSERT_EQ(settings.min_urgency, etalon_k2 + 16);
  ASSERT_EQ(settings.wave_thickness_minutes, etalon_k2 + 21);
  ASSERT_EQ(settings.paid_supply_max_search_route_distance, etalon_k2 + 55);
  ASSERT_EQ(settings.paid_supply_max_line_distance, etalon_k2 + 56);
  ASSERT_EQ(settings.paid_supply_max_search_route_time, etalon_k2 + 57);
  dynamic_config::ValueDict<models::SettingsValues::PedestrianSettings>
      true_value{"",
                 {{"bicycle",
                   models::SettingsValues::PedestrianSettings{
                       static_cast<uint32_t>(etalon_k2 + 40),  //
                       static_cast<uint32_t>(etalon_k2 + 41),  //
                       std::chrono::seconds(etalon_k2 + 42),   //
                       static_cast<uint32_t>(etalon_k2 + 43),  //
                       std::chrono::seconds(etalon_k2 + 44)    //
                   }},
                  {"pedestrian", models::SettingsValues::PedestrianSettings{
                                     static_cast<uint32_t>(etalon_k2 + 49),  //
                                     static_cast<uint32_t>(etalon_k2 + 50),  //
                                     std::chrono::seconds(etalon_k2 + 51),   //
                                     static_cast<uint32_t>(etalon_k2 + 52),  //
                                     std::chrono::seconds(etalon_k2 + 53)    //
                                 }}}};
  ASSERT_EQ(settings.pedestrian_settings, true_value);

  // paid supply allowed
  params.is_paid_supply = true;
  settings = service_settings.FetchPrepared(params);
  ASSERT_EQ(settings.query_limit_limit, etalon_k2 + 35);
  ASSERT_EQ(settings.query_limit_free_preferred, etalon_k2 + 34);
  ASSERT_EQ(settings.query_limit_free_preferred_eta, etalon_k2 + 51);
  ASSERT_EQ(settings.query_limit_limit_eta, etalon_k2 + 52);
  ASSERT_EQ(settings.query_limit_max_line_dist, etalon_k2 + 36);
  ASSERT_TRUE(CompareDouble(settings.max_robot_distance, etalon_k2 + 55));
  ASSERT_TRUE(CompareDouble(settings.max_robot_time, etalon_k2 + 57));
  ASSERT_EQ(settings.order_chain_max_line_distance, etalon_k1 + 29);
  ASSERT_EQ(settings.order_chain_max_route_distance, etalon_k1 + 30);
  ASSERT_EQ(settings.order_chain_max_route_time, etalon_k1 + 31);
  ASSERT_EQ(settings.order_chain_max_total_time, etalon_k1 + 59);
  ASSERT_EQ(settings.order_chain_max_total_distance, etalon_k1 + 60);
  ASSERT_EQ(settings.no_reposition_preferred, etalon_k2 + 39);
  ASSERT_EQ(settings.chain_preferred, etalon_k2 + 46);
  ASSERT_EQ(settings.same_park_preferred, etalon_k2 + 47);
  ASSERT_EQ(settings.combo_preferred, etalon_k2 + 58);
  ASSERT_EQ(settings.min_urgency, etalon_k2 + 16);
  ASSERT_EQ(settings.wave_thickness_minutes, etalon_k2 + 21);
  ASSERT_EQ(settings.paid_supply_max_search_route_distance, etalon_k2 + 55);
  ASSERT_EQ(settings.paid_supply_max_line_distance, etalon_k2 + 56);
  ASSERT_EQ(settings.paid_supply_max_search_route_time, etalon_k2 + 57);

  // paid supply + eta
  params.is_for_eta = true;
  settings = service_settings.FetchPrepared(params);
  ASSERT_EQ(settings.query_limit_free_preferred, etalon_k2 + 51);
  ASSERT_EQ(settings.query_limit_limit, etalon_k2 + 52);
  ASSERT_EQ(settings.query_limit_free_preferred_eta, etalon_k2 + 51);
  ASSERT_EQ(settings.query_limit_limit_eta, etalon_k2 + 52);
  ASSERT_EQ(settings.query_limit_max_line_dist, etalon_k2 + 55);
  ASSERT_TRUE(CompareDouble(settings.max_robot_distance, etalon_k2 + 55));
  ASSERT_TRUE(CompareDouble(settings.max_robot_time, etalon_k2 + 57));
  ASSERT_EQ(settings.order_chain_max_line_distance, etalon_k1 + 29);
  ASSERT_EQ(settings.order_chain_max_route_distance, etalon_k1 + 30);
  ASSERT_EQ(settings.order_chain_max_route_time, etalon_k1 + 31);
  ASSERT_EQ(settings.order_chain_max_total_time, etalon_k1 + 59);
  ASSERT_EQ(settings.order_chain_max_total_distance, etalon_k1 + 60);
  ASSERT_EQ(settings.no_reposition_preferred, etalon_k2 + 39);
  ASSERT_EQ(settings.chain_preferred, etalon_k2 + 46);
  ASSERT_EQ(settings.same_park_preferred, etalon_k2 + 47);
  ASSERT_EQ(settings.combo_preferred, etalon_k2 + 58);
  ASSERT_EQ(settings.min_urgency, etalon_k2 + 16);
  ASSERT_EQ(settings.wave_thickness_minutes, etalon_k2 + 21);
  ASSERT_EQ(settings.paid_supply_max_search_route_distance, etalon_k2 + 55);
  ASSERT_EQ(settings.paid_supply_max_line_distance, etalon_k2 + 56);
  ASSERT_EQ(settings.paid_supply_max_search_route_time, etalon_k2 + 57);
}

TEST(DispatchSettings, PedestrianSettingsDefault) {
  dynamic_config::ValueDict<models::SettingsValues::PedestrianSettings>
      true_value{"",
                 {{"__default__", models::SettingsValues::PedestrianSettings{
                                      2000,                        //
                                      std::nullopt,                //
                                      std::nullopt,                //
                                      15000,                       //
                                      std::chrono::seconds(10800)  //
                                  }}}};

  models::SettingsValues settings_values;
  ASSERT_EQ(settings_values.pedestrian_settings, true_value);
}

}  // namespace dispatch_settings::test
