#include "models_test.hpp"

#include "tests/core/models_test.hpp"
#include "tests/internal/models_test.hpp"

namespace sweet_home::plaque {

std::unordered_map<std::string, Widget> PrepareWidgets() {
  Widget balance_without_text;
  balance_without_text.widget_id = "widget:common:balance_without_text";
  balance_without_text.type = WidgetType::kBalance;
  balance_without_text.balance_ = BalanceWidget{};

  Widget buy_plus;
  buy_plus.widget_id = "widget:common:buy_plus";
  buy_plus.type = WidgetType::kButton;
  buy_plus.button_ = ButtonWidget{
      tests::MakeTranslationData("sweet_home.plaque.widgets.buy_plus.text")};

  Widget composite_payment;
  composite_payment.widget_id = "widget:taxi:composite_payment";
  composite_payment.type = WidgetType::kSwitch;
  composite_payment.switch_ = SwitchWidget{tests::MakeTranslationData(
      "sweet_home.plaque.widgets.composite_payment.text")};
  composite_payment.action =
      tests::MakeChangeSettingAction("composite_payment.enabled");

  Widget plus_burn;
  plus_burn.widget_id = "widget:taxi:plus_burn";
  plus_burn.type = WidgetType::kText;
  plus_burn.text_ = TextWidget{
      tests::MakeTranslationData("sweet_home.plaque.widgets.plus_burn.text")};
  plus_burn.action = tests::MakeOpenDeeplinkAction("yandextaxi://plus_burns");

  Widget catching_up_cashback_text;
  catching_up_cashback_text.widget_id = "widget:taxi:catching_up_cashback_text";
  catching_up_cashback_text.type = WidgetType::kText;
  catching_up_cashback_text.text_ = {
      tests::MakeTranslationData(
          "sweet_home.plaque.widgets.catching_up_cashback.text"),
      tests::MakeAttributedTranslationData(
          "sweet_home.plaque.widgets.catching_up_cashback.text")};

  Widget catching_up_cashback_after_buy_plus_horizont_text;
  catching_up_cashback_after_buy_plus_horizont_text.widget_id =
      "widget:taxi:catching_up_cashback:after_buy_plus:horizont_text";
  catching_up_cashback_after_buy_plus_horizont_text.type =
      WidgetType::kHorizontText;
  HorizontTextWidget horizont_text_widget;
  horizont_text_widget.text_left = tests::MakeAttributedTranslationData(
      "sweet_home.plaque.widgets.catching_up_cashback.after_buy_plus.text_"
      "left");
  horizont_text_widget.text_right = tests::MakeAttributedTranslationData(
      "sweet_home.plaque.widgets.catching_up_cashback.after_buy_plus.text_"
      "right");
  catching_up_cashback_after_buy_plus_horizont_text.horizont_text_ =
      horizont_text_widget;

  return {{balance_without_text.widget_id, balance_without_text},
          {buy_plus.widget_id, buy_plus},
          {composite_payment.widget_id, composite_payment},
          {catching_up_cashback_text.widget_id, catching_up_cashback_text},
          {catching_up_cashback_after_buy_plus_horizont_text.widget_id,
           catching_up_cashback_after_buy_plus_horizont_text},
          {plus_burn.widget_id, plus_burn}};
}

std::unordered_map<std::string, Plaque> PreparePlaques(
    const std::unordered_map<std::string, Widget>& widgets) {
  Plaque buy_plus;
  buy_plus.plaque_id = "plaque:global:buy_plus";
  buy_plus.layout = Layout::kVertical;
  buy_plus.widgets = {widgets.at("widget:common:balance_without_text"),
                      widgets.at("widget:common:buy_plus")};

  buy_plus.condition = SimpleCondition{};
  buy_plus.condition.screens = {"main"};

  buy_plus.priority = 10;

  buy_plus.params = DisplayParams{};
  buy_plus.params.show_after = 10;
  buy_plus.params.close_after = 60;

  buy_plus.requirements = tests::MakeRequirements({{"has_plus", false}});

  Plaque composite_payment;
  composite_payment.plaque_id = "plaque:taxi:composite_payment";
  composite_payment.layout = Layout::kVertical;
  composite_payment.widgets = {widgets.at("widget:common:balance_without_text"),
                               widgets.at("widget:taxi:composite_payment")};

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
  plus_burns.layout = Layout::kVertical;
  plus_burns.widgets = {widgets.at("widget:common:balance_without_text"),
                        widgets.at("widget:taxi:plus_burn")};

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
  catching_up_cashback_text.layout = Layout::kVertical;
  catching_up_cashback_text.widgets = {
      widgets.at("widget:taxi:catching_up_cashback_text")};

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
  catching_up_cashback_after_buy_plus_horizont_text.layout = Layout::kVertical;
  catching_up_cashback_after_buy_plus_horizont_text.widgets = {widgets.at(
      "widget:taxi:catching_up_cashback:after_buy_plus:horizont_text")};

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

}  // namespace sweet_home::plaque
