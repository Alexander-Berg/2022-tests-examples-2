#include <gtest/gtest.h>

#include "tests/core/models_test.hpp"

#include "models_test.hpp"

#include <fmt/format.h>

namespace plus_plaque {

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

}  // namespace plus_plaque

namespace plus_plaque::tests {

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

}  // namespace plus_plaque::tests

namespace plus_plaque::actions {

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

}  // namespace plus_plaque::actions

namespace plus_plaque::requirements {

bool operator==(const ApplicationRequirements& left,
                const ApplicationRequirements& right) {
  return left.app_name == right.app_name &&
         left.should_be_installed == right.should_be_installed;
}

void AssertRequirements(const Requirements& left, const Requirements& right) {
  AssertOptionalEq(left.has_plus, right.has_plus);
  AssertOptionalEq(left.has_cashback_offer, right.has_cashback_offer);
  AssertOptionalEq(left.has_positive_balance, right.has_positive_balance);
  AssertOptionalEq(left.required_experiment, right.required_experiment);
  ASSERT_EQ(left.app_requirements, right.app_requirements);
}

}  // namespace plus_plaque::requirements

namespace plus_plaque::plaque {

void AssertOpacity(const std::optional<Opacity>& left,
                   const std::optional<Opacity>& right) {
  SCOPED_TRACE(__FUNCTION__);

  if (!left && !right) return;
  ValidateOptionalsState(left, right);
  ASSERT_EQ(left->value, right->value);
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

void AssertBalanceWidget(const std::optional<BalanceWidget>& widget,
                         const std::optional<BalanceWidget>& expected) {
  SCOPED_TRACE(__FUNCTION__);

  ASSERT_TRUE(widget);
  ASSERT_TRUE(expected);
  if (expected->title) {
    AssertTranslationData(*widget->title, *expected->title);
  } else {
    ASSERT_FALSE(widget->title);
  }
  if (expected->subtitle) {
    AssertTranslationData(*widget->subtitle, *expected->subtitle);
  } else {
    ASSERT_FALSE(widget->subtitle);
  }
}

void AssertColor(const Color& color, const Color& expected) {
  SCOPED_TRACE(__FUNCTION__);

  ASSERT_EQ(color.color, expected.color);
  ASSERT_EQ(color.opacity.value, expected.opacity.value);
  ASSERT_EQ(color.position, expected.position);
}

void AssertLinearColorSettings(const LinearColorSettings& color_settings,
                               const LinearColorSettings& expected) {
  SCOPED_TRACE(__FUNCTION__);

  ASSERT_EQ(color_settings.colors.size(), expected.colors.size());
  for (size_t i = 0; i < color_settings.colors.size(); ++i) {
    SCOPED_TRACE(fmt::format("Display rules, color: #{}", i));
    AssertColor(color_settings.colors[i], expected.colors[i]);
  }

  ASSERT_EQ(color_settings.start_point, expected.start_point);
  ASSERT_EQ(color_settings.end_point, expected.end_point);
}

void AssertRadialColorSettings(const RadialColorSettings& color_settings,
                               const RadialColorSettings& expected) {
  SCOPED_TRACE(__FUNCTION__);

  ASSERT_EQ(color_settings.colors.size(), expected.colors.size());
  for (size_t i = 0; i < color_settings.colors.size(); ++i) {
    SCOPED_TRACE(fmt::format("Display rules, color: #{}", i));
    AssertColor(color_settings.colors[i], expected.colors[i]);
  }

  ASSERT_EQ(color_settings.central_point, expected.central_point);
}

void AssertCornerSettings(const CornerSettings& corner,
                          const CornerSettings& expected) {
  SCOPED_TRACE(__FUNCTION__);
  LOG_INFO() << "AAAAAA " << int(corner.type) << " " << int(expected.type);
  ASSERT_EQ(corner.type, expected.type);
  if (corner.height_fix) {
    ASSERT_TRUE(expected.height_fix);
    ASSERT_EQ(*corner.height_fix, *expected.height_fix);
  } else {
    ASSERT_FALSE(expected.height_fix);
  }
}

void AssertDisplayRules(const DisplayRules& display_rules,
                        const DisplayRules& expected) {
  SCOPED_TRACE(__FUNCTION__);

  AssertCornerSettings(display_rules.background_shape_settings.right_top_corner,
                       expected.background_shape_settings.right_top_corner);
  AssertCornerSettings(
      display_rules.background_shape_settings.right_bottom_corner,
      expected.background_shape_settings.right_bottom_corner);
  AssertCornerSettings(display_rules.background_shape_settings.left_top_corner,
                       expected.background_shape_settings.left_top_corner);
  AssertCornerSettings(
      display_rules.background_shape_settings.left_bottom_corner,
      expected.background_shape_settings.left_bottom_corner);

  ASSERT_EQ(display_rules.indent_rules.indent_left,
            expected.indent_rules.indent_left);
  ASSERT_EQ(display_rules.indent_rules.indent_right,
            expected.indent_rules.indent_right);
  ASSERT_EQ(display_rules.indent_rules.indent_bottom,
            expected.indent_rules.indent_bottom);
  ASSERT_EQ(display_rules.indent_rules.indent_top,
            expected.indent_rules.indent_top);

  auto colors = display_rules.background_color_settings;
  auto expected_colors = expected.background_color_settings;
  ASSERT_EQ(colors.size(), expected_colors.size());
  for (size_t i = 0; i < colors.size(); ++i) {
    switch (colors[i].type) {
      case ColorSettingsType::kTransparent: {
        SCOPED_TRACE("AssertTransparent");

        ASSERT_EQ(expected_colors[i].type, ColorSettingsType::kTransparent);
        break;
      }
      case ColorSettingsType::kRadial: {
        SCOPED_TRACE("AssertRadial");

        ASSERT_EQ(expected_colors[i].type, ColorSettingsType::kRadial);
        AssertRadialColorSettings(*colors[i].radial,
                                  *expected_colors[i].radial);
        break;
      }
      case ColorSettingsType::kLinear: {
        SCOPED_TRACE("AssertLinear");

        ASSERT_EQ(expected_colors[i].type, ColorSettingsType::kLinear);
        AssertLinearColorSettings(*colors[i].linear,
                                  *expected_colors[i].linear);
        break;
      }
    }
  }
}

void AssertDisplayWidgetRules(const DisplayWidgetRules& widget,
                              const DisplayWidgetRules& expected) {
  SCOPED_TRACE(__FUNCTION__);

  ASSERT_EQ(widget.type, expected.type);
  AssertOpacity(widget.opacity, expected.opacity);
  AssertOptionalEq(widget.width_fix, expected.width_fix);
  AssertOptionalEq(widget.vertical_rule, expected.vertical_rule);
  AssertOptionalEq(widget.horizontal_rule, expected.horizontal_rule);
  AssertDisplayRules(widget.display_rules, expected.display_rules);
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
      AssertTranslationData(widget.button_->text, expected.button_->text);
      break;
    }

    case WidgetType::kSwitch: {
      SCOPED_TRACE("AssertSwitchWidget");

      ASSERT_TRUE(widget.switch_);
      ASSERT_TRUE(expected.switch_);
      AssertTranslationData(widget.switch_->text, expected.switch_->text);
      break;
    }

    case WidgetType::kBalance: {
      AssertBalanceWidget(widget.balance_, expected.balance_);
      break;
    }

    case WidgetType::kText: {
      SCOPED_TRACE("AssertTextWidget");
      ASSERT_TRUE(widget.text_);
      ASSERT_TRUE(expected.text_);
      AssertTranslationData(widget.text_->text, expected.text_->text);
      break;
    }

    case WidgetType::kSpacer: {
      SCOPED_TRACE("AssertSpacerWidget");
      ASSERT_EQ(widget.type, expected.type);
      break;
    }

    case WidgetType::kIcon: {
      SCOPED_TRACE("AssertIconWidget");
      ASSERT_TRUE(widget.icon_);
      ASSERT_TRUE(expected.icon_);
      ASSERT_EQ(widget.icon_->image, expected.icon_->image);
    }
  }
  AssertDisplayWidgetRules(widget.display_widget_rules,
                           expected.display_widget_rules);
  AssertAction(widget.action, expected.action);
}

void AssertWidgetGroup(const WidgetGroup& widget_group,
                       const WidgetGroup& expected) {
  SCOPED_TRACE(testing::Message() << "Assert WidgetGroup with id: "
                                  << widget_group.widget_group_id);

  ASSERT_EQ(widget_group.widget_group_id, expected.widget_group_id);
  AssertDisplayRules(widget_group.display_rules, expected.display_rules);
  ASSERT_EQ(widget_group.widgets.size(), expected.widgets.size());
  for (size_t i = 0; i < widget_group.widgets.size(); ++i) {
    AssertWidget(widget_group.widgets[i], expected.widgets[i]);
  }
}

void AssertElementLevel(const ElementLevel& element,
                        const ElementLevel& expected) {
  SCOPED_TRACE(testing::Message() << "Assert ElementLevel ");

  ASSERT_EQ(element.type, expected.type);

  switch (element.type) {
    case ElementLevelType::kWidget: {
      SCOPED_TRACE("AssertWidgetElementLevel");

      ASSERT_TRUE(element.widget);
      ASSERT_TRUE(expected.widget);
      AssertWidget(*element.widget, *expected.widget);
      break;
    }

    case ElementLevelType::kWidgetGroup: {
      SCOPED_TRACE("AssertWidgetGroupElementLevel");

      ASSERT_TRUE(element.widget_group);
      ASSERT_TRUE(expected.widget_group);
      AssertWidgetGroup(*element.widget_group, *expected.widget_group);
      break;
    }
  }
}

void AssertTariffs(const std::optional<std::vector<Tariff>>& left,
                   const std::optional<std::vector<Tariff>>& right) {
  if (!left || !right) {
    ASSERT_EQ(left, std::nullopt);
    ASSERT_EQ(right, std::nullopt);
    return;
  }

  for (size_t i = 0; i < left->size(); ++i) {
    ASSERT_EQ((*left)[i].vertical, (*right)[i].vertical);
    ASSERT_EQ((*left)[i].tariff, (*right)[i].tariff);
  }
}

void AssertCondition(const SimpleCondition& left,
                     const SimpleCondition& right) {
  ASSERT_EQ(left.screens, right.screens);
  ASSERT_EQ(left.order_states, right.order_states);
  ASSERT_EQ(left.tariffs, right.tariffs);
  AssertTariffs(left.selected_tariffs, right.selected_tariffs);
  AssertTariffs(left.available_tariffs, right.available_tariffs);
  ASSERT_EQ(left.payment_methods, right.payment_methods);
}

void AssertParams(const DisplayParams& left, const DisplayParams& right) {
  ASSERT_EQ(left.show_after, right.show_after);
  ASSERT_EQ(left.close_after, right.close_after);
}

void AssertWidgetsLevel(const WidgetsLevel& left, const WidgetsLevel& right) {
  SCOPED_TRACE(__FUNCTION__);

  ASSERT_EQ(left.elements.size(), right.elements.size());
  ASSERT_EQ(left.widgets_level_id, right.widgets_level_id);
  for (size_t i = 0; i < left.elements.size(); ++i) {
    SCOPED_TRACE(fmt::format("Widgets level element_id #{}", i));
    AssertElementLevel(left.elements[i], right.elements[i]);
  }
  AssertDisplayRules(left.display_rules, right.display_rules);
}

void AssertPlaque(const Plaque& left, const Plaque& right) {
  SCOPED_TRACE(__FUNCTION__);

  ASSERT_EQ(left.plaque_id, right.plaque_id);

  ASSERT_EQ(left.widgets_level.size(), right.widgets_level.size());
  for (size_t i = 0; i < left.widgets_level.size(); i++) {
    SCOPED_TRACE(fmt::format("Plaque widget_level #{}", i));

    AssertWidgetsLevel(left.widgets_level[i], right.widgets_level[i]);
  }

  AssertCondition(left.condition, right.condition);
  ASSERT_EQ(left.priority, right.priority);
  AssertParams(left.params, right.params);
  AssertDisplayRules(left.display_rules, right.display_rules);
  AssertRequirements(left.requirements, right.requirements);
}

}  // namespace plus_plaque::plaque
