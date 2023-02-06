#pragma once

#include "use_cases/user_preferences_change/output_models.hpp"

namespace sweet_home::tests::output_models {

user_preferences_change::output_models::Preference MakePreference(
    std::string setting_id, setting::SettingsValueVariant value,
    setting::SettingType type, bool enabled, bool is_local);

void AssertPreference(
    const user_preferences_change::output_models::Preference& left,
    const user_preferences_change::output_models::Preference& right);

}  // namespace sweet_home::tests::output_models
