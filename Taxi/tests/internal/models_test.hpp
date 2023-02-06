#pragma once

#include <internal/plaque/models.hpp>

#include "core/translator.hpp"

namespace plus_plaque::tests {

namespace defaults {
const std::string kYandexUid = "some_uid";
}  // namespace defaults

requirements::Requirements MakeRequirements(
    const std::unordered_map<std::string, bool>& requirements);

actions::Action MakeChangeSettingAction(const std::string& setting_id);
actions::Action MakeOpenUrlAction(const std::string& url,
                                  bool need_auth = false);
actions::Action MakeOpenDeeplinkAction(const std::string& deeplink);

}  // namespace plus_plaque::tests

namespace plus_plaque::actions {

void AssertAction(
    const Action& action, ActionType expected_type,
    const std::string& expected_content,
    const std::optional<std::string>& plus_context = std::nullopt,
    const std::optional<std::vector<std::string>>& templates = std::nullopt);

}

namespace plus_plaque::plaque {

void AssertPlaque(const Plaque& left, const Plaque& right);

}  // namespace plus_plaque::plaque
