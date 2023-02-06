#include <fmt/format.h>

#include <set>

#include <userver/utest/utest.hpp>

#include <json-diff/json_diff.hpp>

#include "presenters/sdk-state-plaques/plaque.hpp"

#include "tests/internal/plaque/models_test.hpp"
#include "tests/mocks/attributed_translator_service.hpp"
#include "tests/mocks/translator_service.hpp"

namespace plus_plaque::presenters {

namespace {

const std::string kExpectedJson = R"(
{
  "widgets_levels": [
    {
      "widgets_level_id": "level:widget:common:balance",
      "elements": [
        {
          "type": "widget",
          "widget_id": "widget:common:balance"
        }
      ],
      "display_rules": {
        "indent_rules": {
          "indent_left": 0,
          "indent_right": 5,
          "indent_bottom": 10,
          "indent_top": 15
        },
        "background_color_settings": [
          {
            "type": "LINEAR",
            "linear": {
              "colors": [
                {
                  "color": "#00CA50",
                  "position": 0.5,
                  "opacity": 70
                }
              ],
              "start_point": [
                0,
                0
              ],
              "end_point": [
                1,
                1
              ]
            }
          }
        ],
        "background_shape_settings":{
          "left_top_corner":{
            "type": "fix",
            "height_fix": 10
          },
          "right_top_corner":{
            "type": "fix",
            "height_fix": 10
          },
          "left_bottom_corner":{
            "type": "fix",
            "height_fix": 10
          },
          "right_bottom_corner":{
            "type": "half_height"
          }
        }
      }
    },
    {
      "widgets_level_id": "level:widget:common:buy_plus",
      "elements": [
        {
          "type": "widget",
          "widget_id": "widget:common:buy_plus"
        }
      ],
      "display_rules": {
        "indent_rules": {
          "indent_left": 0,
          "indent_right": 5,
          "indent_bottom": 10,
          "indent_top": 15
        },
        "background_color_settings": [
          {
            "type": "LINEAR",
            "linear": {
              "colors": [
                {
                  "color": "#00CA50",
                  "position": 0.5,
                  "opacity": 70
                }
              ],
              "start_point": [
                0,
                0
              ],
              "end_point": [
                1,
                1
              ]
            }
          }
        ],
        "background_shape_settings":{
          "left_top_corner":{
            "type": "fix",
            "height_fix": 10
          },
          "right_top_corner":{
            "type": "fix",
            "height_fix": 10
          },
          "left_bottom_corner":{
            "type": "fix",
            "height_fix": 10
          },
          "right_bottom_corner":{
            "type": "half_height"
          }
        }
      }
    },
    {
      "widgets_level_id": "level:widget:taxi:composite_payment",
      "elements": [
        {
          "type": "widget",
          "widget_id": "widget:taxi:composite_payment"
        }
      ],
      "display_rules": {
        "indent_rules": {
          "indent_left": 0,
          "indent_right": 5,
          "indent_bottom": 10,
          "indent_top": 15
        },
        "background_color_settings": [
          {
            "type": "LINEAR",
            "linear": {
              "colors": [
                {
                  "color": "#00CA50",
                  "position": 0.5,
                  "opacity": 70
                }
              ],
              "start_point": [
                0,
                0
              ],
              "end_point": [
                1,
                1
              ]
            }
          }
        ],
        "background_shape_settings":{
          "left_top_corner":{
            "type": "fix",
            "height_fix": 10
          },
          "right_top_corner":{
            "type": "fix",
            "height_fix": 10
          },
          "left_bottom_corner":{
            "type": "fix",
            "height_fix": 10
          },
          "right_bottom_corner":{
            "type": "half_height"
          }
        }
      }
    }
  ],
  "widgets": [
    {
      "widget_id": "widget:common:balance",
      "display_widget_rules": {
        "width_type": "fit",
        "display_rules": {
          "indent_rules": {
            "indent_left": 0,
            "indent_right": 5,
            "indent_bottom": 10,
            "indent_top": 15
          },
          "background_color_settings": [
            {
              "type": "LINEAR",
              "linear": {
                "colors": [
                  {
                    "color": "#00CA50",
                    "position": 0.5,
                    "opacity": 70
                  }
                ],
                "start_point": [
                  0,
                  0
                ],
                "end_point": [
                  1,
                  1
                ]
              }
            }
          ],
          "background_shape_settings":{
            "left_top_corner":{
              "type": "fix",
              "height_fix": 10
            },
            "right_top_corner":{
              "type": "fix",
              "height_fix": 10
            },
            "left_bottom_corner":{
              "type": "fix",
              "height_fix": 10
            },
            "right_bottom_corner":{
              "type": "half_height"
            }
          }
        },
        "horizontal_rule": "CENTER",
        "vertical_rule": "CENTER"
      },
      "type": "BALANCE",
      "balance": {
        "balance": {
          "items": [
            {
              "type": "text",
              "text": "balance.text/RU"
            }
          ]
        }
      }
    },
    {
      "widget_id": "widget:common:buy_plus",
      "display_widget_rules": {
        "width_type": "fix",
        "width_fix": 50,
        "display_rules": {
          "indent_rules": {
            "indent_left": 0,
            "indent_right": 5,
            "indent_bottom": 10,
            "indent_top": 15
          },
          "background_color_settings": [
            {
              "type": "LINEAR",
              "linear": {
                "colors": [
                  {
                    "color": "#00CA50",
                    "position": 0.5,
                    "opacity": 70
                  }
                ],
                "start_point": [
                  0,
                  0
                ],
                "end_point": [
                  1,
                  1
                ]
              }
            }
          ],
          "background_shape_settings":{
            "left_top_corner":{
              "type": "fix",
              "height_fix": 10
            },
            "right_top_corner":{
              "type": "fix",
              "height_fix": 10
            },
            "left_bottom_corner":{
              "type": "fix",
              "height_fix": 10
            },
            "right_bottom_corner":{
              "type": "half_height"
            }
          }
        },
        "horizontal_rule": "RIGHT",
        "vertical_rule": "BOTTOM"
      },
      "type": "BUTTON",
      "button": {
        "text": {
          "items": [
            {
              "type": "text",
              "text": "sweet_home.plaque.widgets.buy_plus.text/RU"
            }
          ]
        }
      }
    },
    {
      "widget_id": "widget:taxi:composite_payment",
      "display_widget_rules": {
        "width_type": "fit",
        "display_rules": {
          "indent_rules": {
            "indent_left": 0,
            "indent_right": 5,
            "indent_bottom": 10,
            "indent_top": 15
          },
          "background_color_settings": [
            {
              "type": "LINEAR",
              "linear": {
                "colors": [
                  {
                    "color": "#00CA50",
                    "position": 0.5,
                    "opacity": 70
                  }
                ],
                "start_point": [
                  0,
                  0
                ],
                "end_point": [
                  1,
                  1
                ]
              }
            }
          ],
          "background_shape_settings":{
            "left_top_corner":{
              "type": "fix",
              "height_fix": 10
            },
            "right_top_corner":{
              "type": "fix",
              "height_fix": 10
            },
            "left_bottom_corner":{
              "type": "fix",
              "height_fix": 10
            },
            "right_bottom_corner":{
              "type": "half_height"
            }
          }
        },
        "horizontal_rule": "CENTER",
        "vertical_rule": "CENTER"
        },
        "type": "SWITCH",
        "switch": {
          "text": {
            "items": [
              {
                "type": "text",
                "text": "sweet_home.plaque.widgets.composite_payment.text/RU"
              }
            ]
          }
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
      "widgets_level_ids": [
        "level:widget:common:balance",
        "level:widget:common:buy_plus"
      ],
      "condition": {
        "screens": [
          "main"
        ],
        "tariffs": ["econom"],
        "selected_tariffs": [{"tariff":"econom","vertical":"taxi"}],
        "available_tariffs": [{"tariff":"econom","vertical":"taxi"}],
        "payment_methods": ["cash","card"]
      },
      "priority": 10,
      "params": {
        "show_after": 10,
        "close_after": 60
      },
      "display_rules": {
        "indent_rules": {
          "indent_left": 0,
          "indent_right": 5,
          "indent_bottom": 10,
          "indent_top": 15
        },
        "background_color_settings": [
          {
            "type": "LINEAR",
            "linear": {
              "colors": [
                {
                  "color": "#00CA50",
                  "position": 0.5,
                  "opacity": 70
                }
              ],
              "start_point": [
                0,
                0
              ],
              "end_point": [
                1,
                1
              ]
            }
          }
        ],
        "background_shape_settings":{
          "left_top_corner":{
            "type": "fix",
            "height_fix": 10
          },
          "right_top_corner":{
            "type": "fix",
            "height_fix": 10
          },
          "left_bottom_corner":{
            "type": "fix",
            "height_fix": 10
          },
          "right_bottom_corner":{
            "type": "half_height"
          }
        }
      },
      "visual_effects": [
        {
          "trigger": "OPEN_PLAQUE",
          "type": "CONFETTI"
        },
        {
          "trigger": "SUCCESS_PURCHASE",
          "type": "CONFETTI"
        },
        {
          "trigger": "WIDGET",
          "type": "CONFETTI",
          "widget": {
            "type": "CLICK",
            "widgets": [
              "1",
              "2"
            ]
          }
        }
      ]
    },
    {
      "plaque_id": "plaque:taxi:composite_payment",
      "widgets_level_ids": [
        "level:widget:common:balance",
        "level:widget:taxi:composite_payment"
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
      },
      "display_rules": {
        "indent_rules": {
          "indent_left": 0,
          "indent_right": 5,
          "indent_bottom": 10,
          "indent_top": 15
        },
        "background_color_settings": [
          {
            "type": "LINEAR",
            "linear": {
              "colors": [
                {
                  "color": "#00CA50",
                  "position": 0.5,
                  "opacity": 70
                }
              ],
              "start_point": [
                0,
                0
              ],
              "end_point": [
                1,
                1
              ]
            }
          }
        ],
        "background_shape_settings":{
          "left_top_corner":{
            "type": "fix",
            "height_fix": 10
          },
          "right_top_corner":{
            "type": "fix",
            "height_fix": 10
          },
          "left_bottom_corner":{
            "type": "fix",
            "height_fix": 10
          },
          "right_bottom_corner":{
            "type": "half_height"
          }
        }
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

  auto attributed_translate_func =
      [](const core::AttributedTranslationData& key, const std::string& locale,
         const std::string&) {
        auto attr_text_obj = extended_template::AttributedText();

        auto attr_text =
            handlers::libraries::extended_template::ATTextProperty();
        attr_text.type =
            handlers::libraries::extended_template::ATTextPropertyType::kText;
        attr_text.text = fmt::format("{}/{}", key.main_key->key, locale);
        attr_text_obj.items.push_back(attr_text);

        return attr_text_obj;
      };

  result.translator = std::make_shared<mocks::TranslatorServiceMock>(
      translate_func, translate_func);
  result.attributed_translator =
      std::make_shared<mocks::AttributedTranslatorServiceMock>(
          attributed_translate_func, attributed_translate_func);
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

  std::set<formats::json::Value, ArrayCmp> sorted_array(ArrayCmp{key});
  for (const auto& json_item : array) {
    sorted_array.insert(json_item);
  }
  return sorted_array;
}

}  // namespace

TEST(TestBuildPlaqueDefinitions, HappyPath) {
  auto widgets = plaque::PrepareWidgets();
  auto widgets_level = plaque::PrepareLevels(widgets);
  auto plaques = plaque::PreparePlaques(widgets_level);

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

  // widgets_levels are composed from unordered_map - they can have different
  // order from run to run
  EXPECT_PRED_FORMAT2(
      json_diff::AreValuesEqual,
      GetSortedArray(result_json["widgets_levels"], "widgets_level_id"),
      GetSortedArray(expected_json["widgets_levels"], "widgets_level_id"));

  // widgets are composed from unordered_map - they can have different order
  // from run to run
  EXPECT_PRED_FORMAT2(json_diff::AreValuesEqual,
                      GetSortedArray(result_json["widgets"], "widget_id"),
                      GetSortedArray(expected_json["widgets"], "widget_id"));
}

}  // namespace plus_plaque::presenters
