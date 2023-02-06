#include "docs_map.hpp"

#include <set>

#include <userver/dynamic_config/fwd.hpp>
#include <userver/dynamic_config/value.hpp>
#include <userver/formats/json.hpp>

namespace parks_activation {

template <class T>
formats::json::Value MakeConfig(T&& value) {
  formats::json::ValueBuilder json = formats::json::Type::kObject;
  json = value;
  return json.ExtractValue();
}

dynamic_config::DocsMap DocsMapForTest(
    bool use_extra_thresholds, bool low_balance_activated,
    const std::unordered_set<std::string>& payment_methods_low_balance,
    bool check_contract_is_finished,
    const std::unordered_map<std::string, ::utils::datetime::Date>&
        netting_subsidy_countries,
    const std::unordered_map<std::string, bool>&
        logistic_threshold_checking_enabled_for_parks,
    std::optional<bool> logistic_threshold_checking_enabled) {
  dynamic_config::DocsMap docs_map;
  docs_map.Set("PARKS_ACTIVATION_PERIODIC_TASK_ENABLED", MakeConfig(true));
  docs_map.Set("PARKS_ACTIVATION_ACTIVATION_HISTORY_ENABLED", MakeConfig(true));
  docs_map.Set("PARKS_ACTIVATION_FIELD_CHANGE_HISTORY_ENABLED",
               MakeConfig(true));
  docs_map.Set("ENABLE_DYNAMIC_PARK_THRESHOLD", MakeConfig(true));
  docs_map.Set("PARKS_ACTIVATION_PERIOD", MakeConfig(35));
  docs_map.Set("PARKS_ACTIVATION_CHUNK_SIZE", MakeConfig(1000));
  docs_map.Set("PARKS_ACTIVATION_DISTLOCK_NAME",
               MakeConfig("parks_activation"));
  docs_map.Set("PARKS_ACTIVATION_DISTLOCK_TIMEOUT", MakeConfig(30));
  docs_map.Set("PARKS_ACTIVATION_GET_OLD_PARKS_DB_TIMEOUT", MakeConfig(1000));
  docs_map.Set("PARKS_ACTIVATION_UPDATE_PARKS_DB_TIMEOUT", MakeConfig(1000));
  docs_map.Set("USE_EXTRA_THRESHOLDS", MakeConfig(use_extra_thresholds));

  formats::json::ValueBuilder threshold_checking_for_parks;
  threshold_checking_for_parks["__default__"] =
      logistic_threshold_checking_enabled &&
      logistic_threshold_checking_enabled.value();
  for (auto& iterator : logistic_threshold_checking_enabled_for_parks) {
    threshold_checking_for_parks[iterator.first] = iterator.second;
  }
  docs_map.Set("PARKS_ACTIVATION_ENABLE_LOGISTIC_THRESHOLD_CHECKING_FOR_PARKS",
               MakeConfig(std::move(threshold_checking_for_parks)));

  formats::json::ValueBuilder extra_threshold_by_countries;
  extra_threshold_by_countries["__default__"] = -1000;
  extra_threshold_by_countries["country1"] = -2000;

  docs_map.Set("EXTRA_THRESHOLDS_BY_COUNTRIES",
               MakeConfig(std::move(extra_threshold_by_countries)));
  formats::json::ValueBuilder payment_methods_low_balance_json =
      formats::json::Type::kArray;
  for (const auto& payment : payment_methods_low_balance) {
    payment_methods_low_balance_json.PushBack(payment);
  }
  docs_map.Set("PARK_LOW_BALANCE_ALLOWED_ENABLED",
               MakeConfig(low_balance_activated));
  docs_map.Set("PARK_LOW_BALANCE_ALLOWED",
               MakeConfig(std::move(payment_methods_low_balance_json)));

  docs_map.Set("PARKS_ACTIVATION_CHECK_CONTRACT_IS_FINISHED",
               MakeConfig(check_contract_is_finished));
  docs_map.Set("BILLING_COUNTRIES_WITH_ORDER_BILLINGS_SUBVENTION_NETTING",
               MakeConfig(netting_subsidy_countries));
  docs_map.Set("PARKS_ACTIVATION_CORP_WITHOUT_VAT_CONTRACT_REQUIRED",
               MakeConfig(true));
  return docs_map;
}

}  // namespace parks_activation
