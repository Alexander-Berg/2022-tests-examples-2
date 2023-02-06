#pragma once

#include <internal/balance_badge/balance_badge.hpp>
#include <internal/client_application/client_application.hpp>
#include <internal/plaque.hpp>
#include <internal/setting/repository.hpp>
#include <internal/subscription/models.hpp>
#include <internal/user_preferences/models.hpp>

#include "core/translator.hpp"

namespace sweet_home::tests {

namespace defaults {
const std::string kYandexUid = "some_uid";
}  // namespace defaults

core::Price MakeSubscriptionPrice(const std::string& price,
                                  const std::string& currency);

subscription::PlusSubscription MakePlusSubscription(
    const std::string& subscription_id, subscription::PurchaseStatus status,
    bool is_cashback,
    const std::optional<core::Price>& subscription_price =
        MakeSubscriptionPrice("199", "RUB"));

requirements::Requirements MakeRequirements(
    const std::unordered_map<std::string, bool>& requirements);

setting::SettingDefinition MakeDefinition(
    const std::string& setting_id, const std::string& value,
    bool is_local = false, bool enabled = true,
    const requirements::Requirements& requirements = {});

setting::SettingDefinition MakeDefinition(
    const std::string& setting_id, setting::SettingType type,
    setting::SettingsValueVariant value, bool is_local = false,
    bool enabled = true, const requirements::Requirements& requirements = {});

setting::SettingDefinitionsMap MakeSettingDefinitionMap(
    const std::vector<setting::SettingDefinition>& definitions);

user_preferences::Preference MakePreference(const std::string& setting_id,
                                            const std::string& value);

user_preferences::Preference MakePreference(
    const std::string& setting_id, setting::SettingType type,
    setting::SettingsValueVariant value);

user_preferences::UserPreferences MakeUserPreferences(
    const std::vector<user_preferences::Preference>& preferences,
    const std::string& version = "some_version",
    const std::string& yandex_uid = defaults::kYandexUid);

}  // namespace sweet_home::tests

namespace sweet_home::subscription {

void AssertPlusSubscription(const PlusSubscription& left,
                            const PlusSubscription& right);

}  // namespace sweet_home::subscription

namespace sweet_home::balance_badge {

bool operator==(const balance_badge::BalanceBadge& left,
                const balance_badge::BalanceBadge& right);

}  // namespace sweet_home::balance_badge

// client_application
namespace sweet_home::tests {

actions::Action MakeChangeSettingAction(const std::string& setting_id);
actions::Action MakeOpenUrlAction(const std::string& url,
                                  bool need_auth = false);
actions::Action MakeOpenDeeplinkAction(const std::string& deeplink);

// most often would have title
client_application::Element MakeLead(
    const std::string& title_key,
    const std::optional<std::string>& subtitle_key = std::nullopt,
    const std::optional<core::Image>& icon = std::nullopt,
    client_application::ElementStyle style =
        client_application::ElementStyle::kDefault);

// most often would have custom style
client_application::Element MakeTrail(
    client_application::ElementStyle style,
    const std::optional<std::string>& title_key = std::nullopt,
    const std::optional<std::string>& subtitle_key = std::nullopt,
    const std::optional<core::Image>& icon = std::nullopt);

// basic maker
client_application::Element MakeElement(
    const std::optional<std::string>& title_key,
    const std::optional<std::string>& subtitle_key = std::nullopt,
    const std::optional<core::Image>& icon = std::nullopt,
    client_application::ElementStyle style =
        client_application::ElementStyle::kDefault);

client_application::MenuItem MakeListItem(
    const actions::Action& action,
    const std::optional<client_application::Element>& lead = std::nullopt,
    const std::optional<client_application::Element>& trail = std::nullopt);

client_application::MenuItem MakeStoriesItem(
    const std::string&, const client_application::Dimensions&);

client_application::Section MakeSection(
    const std::vector<client_application::MenuItem>& items,
    client_application::SectionStyle style =
        client_application::SectionStyle::kNone,
    const std::optional<std::string>& title_key = std::nullopt);

}  // namespace sweet_home::tests

namespace sweet_home::actions {

void AssertAction(
    const Action& action, ActionType expected_type,
    const std::string& expected_content,
    const std::optional<std::string>& plus_context = std::nullopt,
    const std::optional<std::vector<std::string>>& templates = std::nullopt);

}

namespace sweet_home::client_application {

void AssertSizes(const std::vector<Section>& sections,
                 std::vector<size_t> expected_section_sizes);

void AssertElement(const std::optional<Element>& element,
                   ElementStyle expected_style = ElementStyle::kDefault);

void AssertElementWithText(
    const std::optional<Element>& element, const std::string& expected_key,
    ElementStyle expected_style = ElementStyle::kDefault);

}  // namespace sweet_home::client_application

namespace sweet_home::plaque {

void AssertPlaque(const Plaque& left, const Plaque& right);

}  // namespace sweet_home::plaque
