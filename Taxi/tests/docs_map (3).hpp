#pragma once

#include <unordered_set>

#include <userver/dynamic_config/fwd.hpp>
#include <userver/dynamic_config/value.hpp>
#include <userver/utils/datetime/date.hpp>

namespace parks_activation {
dynamic_config::DocsMap DocsMapForTest(
    bool use_extra_thresholds = false, bool low_balance_activated = false,
    const std::unordered_set<std::string>& payment_methods_low_balance = {},
    bool check_contract_is_active = false,
    const std::unordered_map<std::string, ::utils::datetime::Date>&
        netting_subsidy_countries = {},
    const std::unordered_map<std::string, bool>&
        logistic_threshold_checking_enabled_for_parks = {},
    std::optional<bool> logistic_threshold_checking_enabled = {});
}
