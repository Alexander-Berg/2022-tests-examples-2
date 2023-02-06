#include "models_test.hpp"

#include "tests/core/models_test.hpp"
#include "tests/internal/models_test.hpp"

namespace plus_plaque::plaque {

const auto DefaultColorSettings =
    ColorSettings{ColorSettingsType::kLinear,
                  LinearColorSettings{std::vector{Color{"#00CA50", 0.5, {70}}},
                                      std::vector{0., 0.}, std::vector{1., 1.}},
                  std::nullopt};

const auto DefaultShapeSettings =
    ShapeSettings{{CornerSettingsType::kFix, 10},
                  {CornerSettingsType::kFix, 10},
                  {CornerSettingsType::kFix, 10},
                  {CornerSettingsType::kHalfHeight, std::nullopt}};

const auto DefaultDisplayRules = DisplayRules{
    IndentRules{0, 5, 10, 15}, {DefaultColorSettings}, DefaultShapeSettings};

const auto DefaultDisplayWidgetRules =
    DisplayWidgetRules{DisplayWidgetRulesType::kFit,
                       DefaultDisplayRules,
                       Opacity{50},
                       std::nullopt,
                       DisplayWidgetRulesHorizontrule::kCenter,
                       DisplayWidgetRulesVerticalrule::kCenter};

std::unordered_map<std::string, Widget> PrepareWidgets() {
  Widget balance;
  balance.widget_id = "widget:common:balance";
  balance.type = WidgetType::kBalance;
  balance.balance_ =
      BalanceWidget{tests::MakeAttributedTranslationData("balance.text"),
                    std::nullopt, std::nullopt};
  balance.display_widget_rules = DefaultDisplayWidgetRules;

  Widget buy_plus;
  buy_plus.widget_id = "widget:common:buy_plus";
  buy_plus.type = WidgetType::kButton;
  buy_plus.button_ = ButtonWidget{tests::MakeAttributedTranslationData(
      "sweet_home.plaque.widgets.buy_plus.text")};
  buy_plus.display_widget_rules = DefaultDisplayWidgetRules;
  buy_plus.display_widget_rules.horizontal_rule =
      DisplayWidgetRulesHorizontrule::kRight;
  buy_plus.display_widget_rules.vertical_rule =
      DisplayWidgetRulesVerticalrule::kBottom;
  buy_plus.display_widget_rules.type = DisplayWidgetRulesType::kFix;
  buy_plus.display_widget_rules.width_fix = 50;

  Widget composite_payment;
  composite_payment.widget_id = "widget:taxi:composite_payment";
  composite_payment.type = WidgetType::kSwitch;
  composite_payment.switch_ = SwitchWidget{tests::MakeAttributedTranslationData(
      "sweet_home.plaque.widgets.composite_payment.text")};
  composite_payment.action =
      tests::MakeChangeSettingAction("composite_payment.enabled");
  composite_payment.display_widget_rules = DefaultDisplayWidgetRules;

  Widget plus_burn;
  plus_burn.widget_id = "widget:taxi:plus_burn";
  plus_burn.type = WidgetType::kText;
  plus_burn.text_ = TextWidget{tests::MakeAttributedTranslationData(
      "sweet_home.plaque.widgets.plus_burn.text")};
  plus_burn.action = tests::MakeOpenDeeplinkAction("yandextaxi://plus_burns");
  plus_burn.display_widget_rules = DefaultDisplayWidgetRules;

  Widget catching_up_cashback_text;
  catching_up_cashback_text.widget_id = "widget:taxi:catching_up_cashback_text";
  catching_up_cashback_text.type = WidgetType::kText;
  catching_up_cashback_text.text_ =
      TextWidget{tests::MakeAttributedTranslationData(
          "sweet_home.plaque.widgets.catching_up_cashback.text")};
  catching_up_cashback_text.display_widget_rules = DefaultDisplayWidgetRules;
  catching_up_cashback_text.display_widget_rules.horizontal_rule =
      DisplayWidgetRulesHorizontrule::kLeft;
  catching_up_cashback_text.display_widget_rules.vertical_rule =
      DisplayWidgetRulesVerticalrule::kTop;
  catching_up_cashback_text.display_widget_rules.type =
      DisplayWidgetRulesType::kFill;
  catching_up_cashback_text.display_widget_rules.display_rules
      .background_color_settings = {ColorSettings{
      ColorSettingsType::kRadial, std::nullopt,
      RadialColorSettings{std::vector{Color{"#00CA50", 0.5, {70}}},
                          std::vector{0., 0.}}}};

  Widget catching_up_cashback_after_buy_plus_left_text;
  catching_up_cashback_after_buy_plus_left_text.widget_id =
      "widget:taxi:catching_up_cashback:after_buy_plus:left_text";
  catching_up_cashback_after_buy_plus_left_text.type = WidgetType::kText;
  catching_up_cashback_after_buy_plus_left_text.text_ =
      TextWidget{tests::MakeAttributedTranslationData(
          "sweet_home.plaque.widgets.catching_up_cashback.after_buy_plus.text_"
          "left")};
  catching_up_cashback_after_buy_plus_left_text.display_widget_rules =
      DefaultDisplayWidgetRules;
  catching_up_cashback_after_buy_plus_left_text.display_widget_rules
      .display_rules.background_color_settings[0]
      .type = ColorSettingsType::kTransparent;
  catching_up_cashback_after_buy_plus_left_text.display_widget_rules
      .display_rules.background_color_settings[0]
      .linear = std::nullopt;

  Widget catching_up_cashback_after_buy_plus_right_text;
  catching_up_cashback_after_buy_plus_right_text.widget_id =
      "widget:taxi:catching_up_cashback:after_buy_plus:right_text";
  catching_up_cashback_after_buy_plus_right_text.type = WidgetType::kText;
  catching_up_cashback_after_buy_plus_right_text.text_ =
      TextWidget{tests::MakeAttributedTranslationData(
          "sweet_home.plaque.widgets.catching_up_cashback.after_buy_plus.text_"
          "right")};
  catching_up_cashback_after_buy_plus_right_text.display_widget_rules =
      DefaultDisplayWidgetRules;

  return {{balance.widget_id, balance},
          {buy_plus.widget_id, buy_plus},
          {composite_payment.widget_id, composite_payment},
          {catching_up_cashback_text.widget_id, catching_up_cashback_text},
          {catching_up_cashback_after_buy_plus_left_text.widget_id,
           catching_up_cashback_after_buy_plus_left_text},
          {catching_up_cashback_after_buy_plus_right_text.widget_id,
           catching_up_cashback_after_buy_plus_right_text},
          {plus_burn.widget_id, plus_burn}};
}

std::unordered_map<std::string, WidgetsLevel> PrepareLevels(
    const std::unordered_map<std::string, Widget>& widgets) {
  WidgetsLevel balance;
  balance.widgets_level_id = "level:widget:common:balance";
  balance.display_rules = DefaultDisplayRules;
  balance.elements = std::vector{
      ElementLevel{ElementLevelType::kWidget,
                   widgets.at("widget:common:balance"), std::nullopt}};

  WidgetsLevel catching_up_cashback_after_buy_plus_horizont_text;
  catching_up_cashback_after_buy_plus_horizont_text.widgets_level_id =
      "level:widget:taxi:catching_up_cashback:after_buy_plus:horizont_text";
  catching_up_cashback_after_buy_plus_horizont_text.display_rules =
      DefaultDisplayRules;
  catching_up_cashback_after_buy_plus_horizont_text
      .elements = std::vector{ElementLevel{
      ElementLevelType::kWidgetGroup, std::nullopt,
      WidgetGroup{
          "group_test",
          {widgets.at(
               "widget:taxi:catching_up_cashback:after_buy_plus:left_text"),
           widgets.at(
               "widget:taxi:catching_up_cashback:after_buy_plus:right_text")},
          DefaultDisplayRules}}};

  WidgetsLevel catching_up_cashback_text;
  catching_up_cashback_text.widgets_level_id =
      "level:widget:taxi:catching_up_cashback_text";
  catching_up_cashback_text.display_rules = DefaultDisplayRules;
  catching_up_cashback_text.elements = std::vector{ElementLevel{
      ElementLevelType::kWidget,
      widgets.at("widget:taxi:catching_up_cashback_text"), std::nullopt}};

  WidgetsLevel buy_plus;
  buy_plus.widgets_level_id = "level:widget:common:buy_plus";
  buy_plus.display_rules = DefaultDisplayRules;
  buy_plus.elements = std::vector{
      ElementLevel{ElementLevelType::kWidget,
                   widgets.at("widget:common:buy_plus"), std::nullopt}};

  WidgetsLevel composite_payment;
  composite_payment.widgets_level_id = "level:widget:taxi:composite_payment";
  composite_payment.display_rules = DefaultDisplayRules;
  composite_payment.elements = std::vector{
      ElementLevel{ElementLevelType::kWidget,
                   widgets.at("widget:taxi:composite_payment"), std::nullopt}};

  WidgetsLevel plus_burn;
  plus_burn.widgets_level_id = "level:widget:taxi:plus_burn";
  plus_burn.display_rules = DefaultDisplayRules;
  plus_burn.elements = std::vector{
      ElementLevel{ElementLevelType::kWidget,
                   widgets.at("widget:taxi:plus_burn"), std::nullopt}};

  return {
      {balance.widgets_level_id, balance},
      {catching_up_cashback_after_buy_plus_horizont_text.widgets_level_id,
       catching_up_cashback_after_buy_plus_horizont_text},
      {catching_up_cashback_text.widgets_level_id, catching_up_cashback_text},
      {buy_plus.widgets_level_id, buy_plus},
      {composite_payment.widgets_level_id, composite_payment},
      {plus_burn.widgets_level_id, plus_burn}};
}

std::unordered_map<std::string, Plaque> PreparePlaques(
    const std::unordered_map<std::string, WidgetsLevel>& widgets_levels) {
  Plaque buy_plus;
  buy_plus.plaque_id = "plaque:global:buy_plus";
  buy_plus.display_rules = DefaultDisplayRules;
  buy_plus.widgets_level = {widgets_levels.at("level:widget:common:balance"),
                            widgets_levels.at("level:widget:common:buy_plus")};

  buy_plus.visual_effects = std::vector{
      VisualEffect{VisualEffectType::kConfetti,
                   VisualEffectTrigger::kOpenPlaque},
      VisualEffect{VisualEffectType::kConfetti,
                   VisualEffectTrigger::kSuccessPurchase},
      VisualEffect{
          VisualEffectType::kConfetti, VisualEffectTrigger::kWidget,
          WidgetVisualEffect{WidgetVisualEffectType::kClick,
                             std::vector{std::string("1"), std::string("2")}}}};

  buy_plus.condition = SimpleCondition{};
  buy_plus.condition.screens = {"main"};
  buy_plus.condition.tariffs = {"econom"};
  std::vector<Tariff> tariffs;
  tariffs.push_back({"taxi", "econom"});
  buy_plus.condition.selected_tariffs = tariffs;
  buy_plus.condition.available_tariffs = tariffs;
  buy_plus.condition.payment_methods = {"cash", "card"};

  buy_plus.priority = 10;

  buy_plus.params = DisplayParams{};
  buy_plus.params.show_after = 10;
  buy_plus.params.close_after = 60;

  buy_plus.requirements = tests::MakeRequirements({{"has_plus", false}});

  Plaque composite_payment;
  composite_payment.plaque_id = "plaque:taxi:composite_payment";
  composite_payment.display_rules = DefaultDisplayRules;
  composite_payment.widgets_level = {
      widgets_levels.at("level:widget:common:balance"),
      widgets_levels.at("level:widget:taxi:composite_payment")};

  composite_payment.condition = SimpleCondition{};
  composite_payment.condition.screens = {"summary"};

  composite_payment.priority = 50;

  composite_payment.params = DisplayParams{};
  composite_payment.params.show_after = 10;
  composite_payment.params.close_after = 60;

  composite_payment.requirements =
      tests::MakeRequirements({{"has_cashback_offer", true},
                               {"has_plus", true},
                               {"has_positive_balance", true}});

  Plaque plus_burns;
  plus_burns.plaque_id = "plaque:taxi:plus_burns";
  plus_burns.display_rules = DefaultDisplayRules;
  plus_burns.widgets_level = {widgets_levels.at("level:widget:common:balance"),
                              widgets_levels.at("level:widget:taxi:plus_burn")};

  plus_burns.condition = SimpleCondition{};
  plus_burns.condition.screens = {"summary"};

  plus_burns.priority = 5;

  plus_burns.params = DisplayParams{};
  plus_burns.params.show_after = 10;
  plus_burns.params.close_after = 60;

  plus_burns.requirements = tests::MakeRequirements(
      {{"has_plus", false}, {"has_positive_balance", true}});

  Plaque catching_up_cashback_text;
  catching_up_cashback_text.plaque_id =
      "plaque:taxi:catching_up_cashback_no_positive_balance";
  catching_up_cashback_text.display_rules = DefaultDisplayRules;
  catching_up_cashback_text.widgets_level = {
      widgets_levels.at("level:widget:taxi:catching_up_cashback_text")};

  catching_up_cashback_text.condition = SimpleCondition{};
  catching_up_cashback_text.condition.screens = {"summary"};

  catching_up_cashback_text.priority = 50;

  catching_up_cashback_text.params = DisplayParams{};
  catching_up_cashback_text.params.show_after = 10;
  catching_up_cashback_text.params.close_after = 60;

  catching_up_cashback_text.requirements = tests::MakeRequirements(
      {{"has_plus", false}, {"has_positive_balance", false}});

  Plaque catching_up_cashback_after_buy_plus_horizont_text;
  catching_up_cashback_after_buy_plus_horizont_text.plaque_id =
      "plaque:taxi:catching_up_cashback_has_positive_balance_success_purchase";
  catching_up_cashback_after_buy_plus_horizont_text.display_rules =
      DefaultDisplayRules;
  catching_up_cashback_after_buy_plus_horizont_text
      .widgets_level = {widgets_levels.at(
      "level:widget:taxi:catching_up_cashback:after_buy_plus:horizont_text")};

  catching_up_cashback_after_buy_plus_horizont_text.condition =
      SimpleCondition{};
  catching_up_cashback_after_buy_plus_horizont_text.condition.screens = {
      "summary"};

  catching_up_cashback_after_buy_plus_horizont_text.priority = 50;

  catching_up_cashback_after_buy_plus_horizont_text.params = DisplayParams{};
  catching_up_cashback_after_buy_plus_horizont_text.params.show_after = 10;
  catching_up_cashback_after_buy_plus_horizont_text.params.close_after = 60;

  catching_up_cashback_after_buy_plus_horizont_text.requirements =
      tests::MakeRequirements(
          {{"has_plus", true}, {"has_positive_balance", true}});

  return {{buy_plus.plaque_id, buy_plus},
          {catching_up_cashback_text.plaque_id, catching_up_cashback_text},
          {catching_up_cashback_after_buy_plus_horizont_text.plaque_id,
           catching_up_cashback_after_buy_plus_horizont_text},
          {composite_payment.plaque_id, composite_payment},
          {plus_burns.plaque_id, plus_burns}};
}

}  // namespace plus_plaque::plaque
