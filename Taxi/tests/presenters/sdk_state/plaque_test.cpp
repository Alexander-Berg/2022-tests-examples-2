
#include <fmt/format.h>

#include <set>

#include <userver/utest/utest.hpp>

#include <json-diff/json_diff.hpp>

#include "presenters/sdk-state/plaque.hpp"

#include "tests/internal/plaque/models_test.hpp"
#include "tests/mocks/translator_service.hpp"

namespace sweet_home::presenters {

namespace {

const std::string kExpectedJson = R"(
{
  "widgets": [
    {
      "widget_id": "widget:common:balance_without_text",
      "type": "BALANCE",
      "balance": {}
    },
    {
      "widget_id": "widget:common:buy_plus",
      "type": "BUTTON",
      "button": {
        "text": "sweet_home.plaque.widgets.buy_plus.text/RU"
      }
    },
    {
      "widget_id": "widget:taxi:composite_payment",
      "type": "SWITCH",
      "switch": {
        "text": "sweet_home.plaque.widgets.composite_payment.text/RU"
      },
      "action": {
        "type": "SETTING",
        "setting_id": "composite_payment.enabled"
      }
    }
  ],
  "plaques": [
    {
      "plaque_id": "plaque:global:buy_plus",
      "layout": "VERTICAL",
      "widgets": [
        "widget:common:balance_without_text",
        "widget:common:buy_plus"
      ],
      "condition": {
        "screens": [
          "main"
        ]
      },
      "priority": 10,
      "params": {
        "show_after": 10,
        "close_after": 60
      }
    },
    {
      "plaque_id": "plaque:taxi:composite_payment",
      "layout": "VERTICAL",
      "widgets": [
        "widget:common:balance_without_text",
        "widget:taxi:composite_payment"
      ],
      "condition": {
        "screens": [
          "summary"
        ]
      },
      "priority": 50,
      "params": {
        "show_after": 10,
        "close_after": 60
      }
    }
  ]
}
)";

}

namespace {

PlaqueContext PrepareContext() {
  PlaqueContext result;
  result.locale = "RU";

  auto translate_func = [](const core::TranslationData& key,
                           const std::string& locale) {
    return fmt::format("{}/{}", key.main_key->key, locale);
  };

  result.translator = std::make_shared<mocks::TranslatorServiceMock>(
      translate_func, translate_func);
  return result;
}

struct ArrayCmp {
  std::string key_;

  bool operator()(const formats::json::Value& lhs,
                  const formats::json::Value& rhs) const {
    return lhs[key_].As<std::string>() < rhs[key_].As<std::string>();
  }
};

std::set<formats::json::Value, ArrayCmp> GetSortedArray(
    const formats::json::Value& array, const std::string& key) {
  if (!array.IsArray()) throw std::runtime_error("value is not an array");

  std::set<formats::json::Value, ArrayCmp> sorted_widgets(ArrayCmp{key});
  for (const auto& json_item : array) {
    sorted_widgets.insert(json_item);
  }
  return sorted_widgets;
}

}  // namespace

TEST(TestBuildPlaqueDefinitions, HappyPath) {
  auto widgets = plaque::PrepareWidgets();
  auto plaques = plaque::PreparePlaques(widgets);

  const std::vector<plaque::Plaque> model{
      plaques["plaque:global:buy_plus"],
      plaques["plaque:taxi:composite_payment"],
  };

  auto context = PrepareContext();
  auto result = BuildPlaqueDefinitions(context, model);

  auto result_json = formats::json::ValueBuilder(result).ExtractValue();
  auto expected_json = formats::json::FromString(kExpectedJson);

  // plaques are always in the same order
  EXPECT_PRED_FORMAT2(json_diff::AreValuesEqual, result_json["plaques"],
                      expected_json["plaques"]);
  // widgets are composed from unordered_map - they can have different order
  // from run to run
  EXPECT_PRED_FORMAT2(json_diff::AreValuesEqual,
                      GetSortedArray(result_json["widgets"], "widget_id"),
                      GetSortedArray(expected_json["widgets"], "widget_id"));
}

}  // namespace sweet_home::presenters
