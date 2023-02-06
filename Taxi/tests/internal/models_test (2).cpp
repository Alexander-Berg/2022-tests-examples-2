#include <gtest/gtest.h>

#include "tests/core/models_test.hpp"

#include "models_test.hpp"

#include <fmt/format.h>

namespace sweet_home {

class OptionalAreEmpty : public std::runtime_error {
 public:
  OptionalAreEmpty() : std::runtime_error("") {}
};

/// @throws OptionalAreEmpty if both left and right are empty. It means that
/// no further checks need to be performed.
template <typename T>
void ValidateOptionalsState(const std::optional<T>& left,
                            const std::optional<T>& right) {
  if (!left && !right) {
    // because std::optional::operator-> doesn't throw any exception on empty
    // object, we could get weird results on testing values of null
    // object's fields. so we need to highlight that both optionals are empty,
    // so no further actions need to be performed.
    throw OptionalAreEmpty();
  }

  SCOPED_TRACE(testing::Message() << "left: " << left.has_value()
                                  << ", right: " << right.has_value());
  if (!left != !right) FAIL();
}

template <typename T>
void AssertOptionalEq(const std::optional<T>& left,
                      const std::optional<T>& right) {
  SCOPED_TRACE(__FUNCTION__);

  if (!left && !right) return;
  ValidateOptionalsState(left, right);
  ASSERT_EQ(*left, *right);
}

}  // namespace sweet_home

namespace sweet_home::tests {

subscription::PlusSubscription MakePlusSubscription(
    const std::string& subscription_id, subscription::PurchaseStatus status,
    bool is_cashback, const std::optional<core::Price>& subscription_price) {
  subscription::PlusSubscription subscription;
  subscription.subscription_id = subscription_id;
  subscription.mediabilling_product_id = "product_" + subscription_id;
  subscription.status = status;
  subscription.is_cashback = is_cashback;
  subscription.price = subscription_price;
  return subscription;
}

core::Price MakeSubscriptionPrice(const std::string& price,
                                  const std::string& currency) {
  return core::Price{decimal64::Decimal<4>::FromStringPermissive(price),
                     currency};
}

requirements::Requirements MakeRequirements(
    const std::unordered_map<std::string, bool>& requirements) {
  requirements::Requirements result;
  if (requirements.count("has_plus")) {
    result.has_plus = requirements.at("has_plus");
  }
  if (requirements.count("has_cashback_offer")) {
    result.has_cashback_offer = requirements.at("has_cashback_offer");
  }
  if (requirements.count("has_positive_balance")) {
    result.has_positive_balance = requirements.at("has_positive_balance");
  }
  return result;
}

setting::SettingDefinition MakeDefinition(
    const std::string& setting_id, const std::string& value, bool is_local,
    bool enabled, const requirements::Requirements& requirements) {
  const auto display_name_key = setting_id + "_key";
  const auto metrica_name = setting_id + "_metrica_name";
  return {setting_id,  display_name_key,
          enabled,     requirements,
          is_local,    {setting::SettingType::kString, value},
          metrica_name};
}

setting::SettingDefinition MakeDefinition(
    const std::string& setting_id, setting::SettingType type,
    setting::SettingsValueVariant value, bool is_local, bool enabled,
    const requirements::Requirements& requirements) {
  const auto display_name_key = setting_id + "_key";
  const auto metrica_name = setting_id + "_metrica_name";

  return {setting_id, display_name_key, enabled,     requirements,
          is_local,   {type, value},    metrica_name};
}

setting::SettingDefinitionsMap MakeSettingDefinitionMap(
    const std::vector<setting::SettingDefinition>& definitions) {
  setting::SettingDefinitionsMap map;
  for (const auto& definition : definitions) {
    map[definition.setting_id] = definition;
  }
  return map;
}

user_preferences::Preference MakePreference(const std::string& setting_id,
                                            const std::string& value) {
  return {setting_id, {setting::SettingType::kString, value}};
}

user_preferences::Preference MakePreference(
    const std::string& setting_id, setting::SettingType type,
    setting::SettingsValueVariant value) {
  return {setting_id, {type, value}};
}

user_preferences::UserPreferences MakeUserPreferences(
    const std::vector<user_preferences::Preference>& preferences,
    const std::string& version, const std::string& yandex_uid) {
  // we have a bug in compiler on bionic, this external declaration
  // is a workaround for it
  auto v = preferences;
  return {yandex_uid, std::move(v), version};
}

actions::Action MakeChangeSettingAction(const std::string& setting_id) {
  actions::Action action;
  action.type = actions::ActionType::kChangeSetting;
  action.setting_id = setting_id;
  return action;
}

actions::Action MakeOpenUrlAction(const std::string& url, bool need_auth) {
  actions::Action action;
  action.type = actions::ActionType::kOpenUrl;
  action.url = url;
  action.need_authorization = need_auth;
  return action;
}

actions::Action MakeOpenDeeplinkAction(const std::string& deeplink) {
  actions::Action action;
  action.type = actions::ActionType::kOpenDeeplink;
  action.deeplink = {deeplink, std::nullopt};
  return action;
}

// most often would have text
client_application::Element MakeLead(
    const std::string& title_key,
    const std::optional<std::string>& subtitle_key,
    const std::optional<core::Image>& icon,
    client_application::ElementStyle style) {
  client_application::Element element;
  element.style = style;
  element.title_key = core::MakeClientKey(title_key);

  if (subtitle_key) {
    element.subtitle_key = core::MakeClientKey(*subtitle_key);
  }

  if (icon) element.icon = *icon;

  return element;
}

// most often would have custom style
client_application::Element MakeTrail(
    client_application::ElementStyle style,
    const std::optional<std::string>& title_key,
    const std::optional<std::string>& subtitle_key,
    const std::optional<core::Image>& icon) {
  client_application::Element element;
  element.style = style;

  if (title_key) {
    element.title_key = core::MakeClientKey(*title_key);
  }
  if (subtitle_key) {
    element.subtitle_key = core::MakeClientKey(*subtitle_key);
  }
  if (icon) {
    element.icon = *icon;
  }

  return element;
}

// basic maker
client_application::Element MakeElement(
    const std::optional<std::string>& title_key,
    const std::optional<std::string>& subtitle_key,
    const std::optional<core::Image>& icon,
    client_application::ElementStyle style) {
  client_application::Element element;
  element.style = style;
  if (title_key) element.title_key = core::MakeClientKey(*title_key);
  if (subtitle_key) element.subtitle_key = core::MakeClientKey(*subtitle_key);
  if (icon) element.icon = *icon;
  return element;
}

client_application::MenuItem MakeListItem(
    const actions::Action& action,
    const std::optional<client_application::Element>& lead,
    const std::optional<client_application::Element>& trail) {
  client_application::ListItem list_item;
  list_item.action = action;
  if (lead) list_item.lead = lead;
  if (trail) list_item.trail = trail;

  client_application::MenuItem menu_item;
  menu_item.type = client_application::MenuItemType::kListItem;

  // TODO: item id from args
  static size_t item_id = 0;
  menu_item.item_id = std::to_string(item_id);
  item_id++;

  menu_item.list_item = list_item;
  return menu_item;
}

client_application::Section MakeSection(
    const std::vector<client_application::MenuItem>& items,
    client_application::SectionStyle style,
    const std::optional<std::string>& title_key) {
  client_application::Section section;
  section.style = style;
  if (title_key) {
    section.title_key = core::MakeClientKey(*title_key);
  }
  section.items = items;
  return section;
}

client_application::MenuItem MakeStoriesItem(
    const std::string& screen, const client_application::Dimensions& dims) {
  client_application::MenuItem result;
  result.type = client_application::MenuItemType::kStories;
  result.item_id = "test_stories_item";
  result.stories = client_application::Stories{screen, dims};
  return result;
}

}  // namespace sweet_home::tests

namespace sweet_home::subscription {

void AssertPlusSubscription(const PlusSubscription& left,
                            const PlusSubscription& right) {
  ASSERT_EQ(left.subscription_id, right.subscription_id);
  ASSERT_EQ(left.mediabilling_product_id, right.mediabilling_product_id);
  ASSERT_EQ(left.status, right.status);
  ASSERT_EQ(left.is_cashback, right.is_cashback);
  core::AssertPrice(left.price, right.price);
}

}  // namespace sweet_home::subscription

namespace sweet_home::balance_badge {

bool operator==(const balance_badge::BalanceBadge& left,
                const balance_badge::BalanceBadge& right) {
  return left.show_glyph == right.show_glyph &&
         left.placeholder == right.placeholder &&
         left.subtitle == right.subtitle;
}

}  // namespace sweet_home::balance_badge

namespace sweet_home::actions {

void AssertAction(const Action& action, ActionType expected_type,
                  const std::string& expected_content,
                  const std::optional<std::string>& plus_context,
                  const std::optional<std::vector<std::string>>& templates) {
  ASSERT_EQ(action.type, expected_type);

  switch (action.type) {
    case ActionType::kSwitchTariff:
      ASSERT_TRUE(action.switch_tariff);
      break;

    case ActionType::kChangeSetting:
      ASSERT_TRUE(action.setting_id);
      ASSERT_EQ(*action.setting_id, expected_content);
      break;

    case ActionType::kOpenDeeplink:
      ASSERT_TRUE(action.deeplink);
      ASSERT_EQ(action.deeplink->deeplink, expected_content);
      break;

    case ActionType::kOpenUrl:
      ASSERT_TRUE(action.url);
      ASSERT_EQ(*action.url, expected_content);
      break;

    case ActionType::kCallSdkHook:
      ASSERT_TRUE(action.hook_id);
      ASSERT_EQ(*action.hook_id, expected_content);
      break;

    case ActionType::kOpenTypedScreen:
      ASSERT_TRUE(action.open_typed_screen_settings);
      ASSERT_EQ(action.open_typed_screen_settings->typed_screen_id,
                expected_content);
      ASSERT_EQ(action.open_typed_screen_settings->plus_context, plus_context);
      ASSERT_EQ(action.open_typed_screen_settings->templates, templates);
  }
}

void AssertAction(const std::optional<Action>& action,
                  const std::optional<Action>& expected) {
  SCOPED_TRACE(__FUNCTION__);

  if (!action && !expected) return;
  ValidateOptionalsState(action, expected);

  ASSERT_EQ(action->type, expected->type);

  switch (action->type) {
    case ActionType::kSwitchTariff: {
      SCOPED_TRACE("AssertSwitchTariff");
      ASSERT_TRUE(action->switch_tariff);
      ASSERT_TRUE(expected->switch_tariff);
      ASSERT_EQ(action->switch_tariff->vertical,
                expected->switch_tariff->vertical);
      ASSERT_EQ(action->switch_tariff->tariff, expected->switch_tariff->tariff);
      break;
    }

    case ActionType::kChangeSetting: {
      SCOPED_TRACE("AssertChangeSetting");
      AssertOptionalEq(action->setting_id, expected->setting_id);
      break;
    }

    case ActionType::kOpenDeeplink: {
      SCOPED_TRACE("AssertOpenDeeplink");
      if (!expected->deeplink) {
        ASSERT_FALSE(action->deeplink);
      } else {
        ASSERT_TRUE(action->deeplink);
        ASSERT_EQ(action->deeplink->deeplink, expected->deeplink->deeplink);
      }
      break;
    }

    case ActionType::kOpenUrl: {
      SCOPED_TRACE("AssertOpenUrl");
      AssertOptionalEq(action->url, expected->url);
      break;
    }

    case ActionType::kCallSdkHook: {
      SCOPED_TRACE("AssertCallSdkHook");
      AssertOptionalEq(action->hook_id, expected->hook_id);
      break;
    }

    case ActionType::kOpenTypedScreen: {
      SCOPED_TRACE("AssertOpenTypedScreen");
      if (!expected->open_typed_screen_settings) {
        ASSERT_FALSE(action->open_typed_screen_settings);
      } else {
        ASSERT_TRUE(action->open_typed_screen_settings);
        const auto& screen_settings = *action->open_typed_screen_settings;
        const auto& expected_screen_settings =
            *expected->open_typed_screen_settings;
        ASSERT_EQ(screen_settings.plus_context,
                  expected_screen_settings.plus_context);
        ASSERT_EQ(screen_settings.templates,
                  expected_screen_settings.templates);
        ASSERT_EQ(screen_settings.typed_screen_id,
                  expected_screen_settings.typed_screen_id);
      }
      break;
    }
  }
}

}  // namespace sweet_home::actions

namespace sweet_home::requirements {

bool operator==(const ApplicationRequirements& left,
                const ApplicationRequirements& right) {
  return left.app_name == right.app_name &&
         left.should_be_installed == right.should_be_installed;
}

void AssertRequirements(const Requirements& left, const Requirements& right) {
  AssertOptionalEq(left.has_plus, right.has_plus);
  AssertOptionalEq(left.has_cashback_offer, right.has_cashback_offer);
  AssertOptionalEq(left.has_positive_balance, right.has_positive_balance);
  AssertOptionalEq(left.has_ability_renew_sub_by_points,
                   right.has_ability_renew_sub_by_points);
  AssertOptionalEq(left.required_experiment, right.required_experiment);
  ASSERT_EQ(left.app_requirements, right.app_requirements);
}

}  // namespace sweet_home::requirements

namespace sweet_home::client_application {

void AssertSizes(const std::vector<Section>& sections,
                 std::vector<size_t> expected_section_sizes) {
  ASSERT_EQ(sections.size(), expected_section_sizes.size());
  for (size_t idx = 0; idx < sections.size(); idx++) {
    ASSERT_EQ(sections[idx].items.size(), expected_section_sizes[idx]);
  }
}

void AssertElement(const std::optional<Element>& element,
                   ElementStyle expected_style) {
  ASSERT_TRUE(element);
  ASSERT_EQ(element->style, expected_style);
}

void AssertElementWithText(const std::optional<Element>& element,
                           const std::string& expected_key,
                           ElementStyle expected_style) {
  ASSERT_TRUE(element) << "Element " << expected_key << " is empty";
  ASSERT_EQ(element->style, expected_style)
      << "Element " << expected_key << " has different style";
  ;

  auto& title_key = element->title_key;
  ASSERT_TRUE(title_key);
  ASSERT_EQ(title_key->key, expected_key);
}

}  // namespace sweet_home::client_application

namespace sweet_home::plaque {

void AssertOpacity(const std::optional<Opacity>& left,
                   const std::optional<Opacity>& right) {
  SCOPED_TRACE(__FUNCTION__);

  if (!left && !right) return;
  ValidateOptionalsState(left, right);
  ASSERT_EQ(left->value, right->value);
}

void AssertBalanceWidget(const std::optional<BalanceWidget>& widget,
                         const std::optional<BalanceWidget>& expected) {
  SCOPED_TRACE(__FUNCTION__);

  ASSERT_TRUE(widget);
  ASSERT_TRUE(expected);

  AssertOptionalEq(widget->title, expected->title);
  AssertOpacity(widget->title_opacity, expected->title_opacity);

  AssertOptionalEq(widget->subtitle, expected->subtitle);
  AssertOpacity(widget->subtitle_opacity, expected->subtitle_opacity);
}

template <typename Text>
void AssertTranslationData(
    const core::BasicTranslationData<Text>& data,
    const core::BasicTranslationData<Text>& expected_data) {
  ASSERT_EQ(data.type, expected_data.type);
  ASSERT_EQ(data.main_key, expected_data.main_key);
  ASSERT_EQ(data.text, expected_data.text);
  ASSERT_EQ(data.fallback_key, expected_data.fallback_key);
}

void AssertWidget(const Widget& widget, const Widget& expected) {
  ASSERT_EQ(widget.widget_id, expected.widget_id);
  SCOPED_TRACE(testing::Message() << "Assert Widget " << widget.widget_id);

  ASSERT_EQ(widget.type, expected.type);

  switch (widget.type) {
    case WidgetType::kButton: {
      SCOPED_TRACE("AssertButtonWidget");

      ASSERT_TRUE(widget.button_);
      ASSERT_TRUE(expected.button_);
      ASSERT_EQ(widget.button_->text, expected.button_->text);
      break;
    }

    case WidgetType::kHorizontText: {
      SCOPED_TRACE("AssertHorizontTextWidget");

      ASSERT_TRUE(widget.horizont_text_);
      ASSERT_TRUE(expected.horizont_text_);
      AssertTranslationData(widget.horizont_text_->text_left,
                            expected.horizont_text_->text_left);
      AssertTranslationData(widget.horizont_text_->text_right,
                            expected.horizont_text_->text_right);
      break;
    }

    case WidgetType::kSwitch: {
      SCOPED_TRACE("AssertSwitchWidget");

      ASSERT_TRUE(widget.switch_);
      ASSERT_TRUE(expected.switch_);
      ASSERT_EQ(widget.switch_->text, expected.switch_->text);
      break;
    }

    case WidgetType::kBalance:
      AssertBalanceWidget(widget.balance_, expected.balance_);
      break;

    case WidgetType::kText:
      SCOPED_TRACE("AssertTextWidget");
      ASSERT_TRUE(widget.text_);
      ASSERT_TRUE(expected.text_);
      AssertTranslationData(widget.text_->text, expected.text_->text);

      if (expected.text_->attributed_text) {
        AssertTranslationData(*widget.text_->attributed_text,
                              *expected.text_->attributed_text);
      } else {
        ASSERT_FALSE(widget.text_->attributed_text);
      }
      break;
  }

  AssertAction(widget.action, expected.action);
}

void AssertCondition(const SimpleCondition& left,
                     const SimpleCondition& right) {
  ASSERT_EQ(left.screens, right.screens);
  ASSERT_EQ(left.order_states, right.order_states);
  ASSERT_EQ(left.tariffs, right.tariffs);
}

void AssertParams(const DisplayParams& left, const DisplayParams& right) {
  ASSERT_EQ(left.show_after, right.show_after);
  ASSERT_EQ(left.close_after, right.close_after);
}

void AssertPlaque(const Plaque& left, const Plaque& right) {
  SCOPED_TRACE(__FUNCTION__);

  ASSERT_EQ(left.plaque_id, right.plaque_id);
  ASSERT_EQ(left.layout, right.layout);

  ASSERT_EQ(left.widgets.size(), right.widgets.size());
  for (size_t i = 0; i < left.widgets.size(); i++) {
    SCOPED_TRACE(fmt::format("Plaque widget #{}", i));

    AssertWidget(left.widgets[i], right.widgets[i]);
  }

  AssertCondition(left.condition, right.condition);
  ASSERT_EQ(left.priority, right.priority);
  AssertParams(left.params, right.params);

  AssertRequirements(left.requirements, right.requirements);
}

}  // namespace sweet_home::plaque
