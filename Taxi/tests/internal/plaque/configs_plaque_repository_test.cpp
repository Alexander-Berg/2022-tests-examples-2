#include <testing/taxi_config.hpp>
#include <userver/formats/json.hpp>
#include <userver/utest/utest.hpp>

#include <taxi_config/variables/PLUS_SWEET_HOME_COLORS.hpp>
#include <taxi_config/variables/PLUS_SWEET_HOME_INDENT_RULES.hpp>
#include <taxi_config/variables/PLUS_SWEET_HOME_PLAQUES_V2_BY_SERVICE.hpp>
#include <taxi_config/variables/PLUS_SWEET_HOME_PLAQUE_V2_WIDGETS.hpp>
#include <taxi_config/variables/PLUS_SWEET_HOME_SHAPE_SETTINGS.hpp>
#include <taxi_config/variables/PLUS_SWEET_HOME_WIDGETS_LEVEL.hpp>
#include <taxi_config/variables/PLUS_SWEET_HOME_WIDGET_GROUPS.hpp>

#include "internal/plaque/impl/configs_plaque_repository.hpp"

#include "models_test.hpp"
#include "tests/internal/models_test.hpp"

namespace plus_plaque::plaque::impl {

namespace {
const std::string kIndentRulesJson = R"(
{
  "default_indent_rules": {
    "indent_left": 0,
    "indent_right": 5,
    "indent_bottom": 10,
    "indent_top": 15
  }
}
)";

const std::string kShapeSettingsJson = R"(
{
  "default_shape_settings": {
    "left_top_corner": {
      "type": "fix",
      "height_fix": 10
    },
    "right_top_corner": {
      "type": "fix",
      "height_fix": 10
    },
    "left_bottom_corner": {
      "type": "fix",
      "height_fix": 10
    },
    "right_bottom_corner": {
      "type": "half_height"
    }
  }
}
)";

const std::string kColorsJson = R"(
{
  "linear_gradient": [
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
        "start_point": [0, 0],
        "end_point": [1, 1]
      }
    }
  ],
  "radial_gradient": [
    {
      "type": "RADIAL",
      "radial": {
        "colors": [
          {
            "color": "#00CA50",
            "position": 0.5,
            "opacity": 70
          }
        ],
        "central_point": [0, 0]
      }
    }
  ],
  "transparent": [
    {
      "type": "TRANSPARENT"
    }
  ]
}
)";

const std::string kWidgetsJson = R"(
{
  "widget:common:balance": {
    "type": "BALANCE",
    "balance": {
      "balance_key": "balance.text"
    },
    "display_widget_rules": {
      "type": "fit",
      "opacity": 50,
      "horizontal_rule": "CENTER",
      "vertical_rule": "CENTER",
      "display_rules": {
        "indent_rules_id": "default_indent_rules",
        "background_color_settings_id": "linear_gradient",
        "background_shape_settings": "default_shape_settings"
      }
    }
  },
  "widget:taxi:catching_up_cashback_text": {
     "type": "TEXT",
     "text": {
        "text_key": "sweet_home.plaque.widgets.catching_up_cashback.text"
     },
      "display_widget_rules": {
        "type": "fill",
        "opacity": 50,
        "horizontal_rule": "LEFT",
        "vertical_rule": "TOP",
        "display_rules": {
          "indent_rules_id": "default_indent_rules",
          "background_color_settings_id": "radial_gradient",
          "background_shape_settings": "default_shape_settings"
        }
      }
  },
  "widget:taxi:catching_up_cashback:after_buy_plus:left_text": {
    "type": "TEXT",
     "text": {
        "text_key": "sweet_home.plaque.widgets.catching_up_cashback.after_buy_plus.text_left"
     },
      "display_widget_rules": {
      "type": "fit",
      "opacity": 50,
      "horizontal_rule": "CENTER",
      "vertical_rule": "CENTER",
      "display_rules": {
        "indent_rules_id": "default_indent_rules",
        "background_color_settings_id": "transparent",
        "background_shape_settings": "default_shape_settings"
      }
    }
  },
  "widget:taxi:catching_up_cashback:after_buy_plus:right_text": {
    "type": "TEXT",
     "text": {
        "text_key": "sweet_home.plaque.widgets.catching_up_cashback.after_buy_plus.text_right"
     },
      "display_widget_rules": {
        "type": "fit",
        "opacity": 50,
        "horizontal_rule": "CENTER",
        "vertical_rule": "CENTER",
        "display_rules": {
          "indent_rules_id": "default_indent_rules",
          "background_color_settings_id": "linear_gradient",
          "background_shape_settings": "default_shape_settings"
        }
      }
  },
  "widget:common:buy_plus": {
    "type": "BUTTON",
    "button": {
      "text_key": "sweet_home.plaque.widgets.buy_plus.text"
    },
    "display_widget_rules": {
      "type": "fix",
      "opacity": 50,
      "width_fix": 50,
      "horizontal_rule": "RIGHT",
      "vertical_rule": "BOTTOM",
      "display_rules": {
        "indent_rules_id": "default_indent_rules",
        "background_color_settings_id": "linear_gradient",
        "background_shape_settings": "default_shape_settings"
      }
    }
  },
  "widget:taxi:composite_payment": {
    "type": "SWITCH",
    "switch": {
      "text_key": "sweet_home.plaque.widgets.composite_payment.text"
    },
    "action": {
      "setting_id": "composite_payment.enabled",
      "type": "SETTING"
    },
    "display_widget_rules": {
      "type": "fit",
      "opacity": 50,
      "horizontal_rule": "CENTER",
      "vertical_rule": "CENTER",
      "display_rules": {
        "indent_rules_id": "default_indent_rules",
        "background_color_settings_id": "linear_gradient",
        "background_shape_settings": "default_shape_settings"
      }
    }
  },
  "widget:taxi:plus_burn": {
    "type": "TEXT",
    "text": {
      "text_key": "sweet_home.plaque.widgets.plus_burn.text"
    },
    "action": {
      "type": "DEEPLINK",
      "deeplink": "yandextaxi://plus_burns"
    },
    "display_widget_rules": {
      "type": "fit",
      "opacity": 50,
      "horizontal_rule": "CENTER",
      "vertical_rule": "CENTER",
      "display_rules": {
        "indent_rules_id": "default_indent_rules",
        "background_color_settings_id": "linear_gradient",
        "background_shape_settings": "default_shape_settings"
      }
    }
  }
}
)";

const std::string kWidgetGroupsJson = R"(
{
  "group_test": {
    "widgets": ["widget:taxi:catching_up_cashback:after_buy_plus:left_text", "widget:taxi:catching_up_cashback:after_buy_plus:right_text"],
    "display_rules": {
      "indent_rules_id": "default_indent_rules",
      "background_color_settings_id": "linear_gradient",
      "background_shape_settings": "default_shape_settings"
    }
  }
}
)";

const std::string kWidgetsLevelsJson = R"(
{
  "level:widget:common:balance": {
    "elements": [
      {
        "type": "widget",
        "widget_id": "widget:common:balance",
        "display_rules": {
          "indent_rules_id": "default_indent_rules",
          "background_color_settings_id": "linear_gradient",
          "background_shape_settings": "default_shape_settings"
        }
      }
    ],
    "display_rules": {
      "indent_rules_id": "default_indent_rules",
      "background_color_settings_id": "linear_gradient",
      "background_shape_settings": "default_shape_settings"
    }
  },
  "level:widget:taxi:catching_up_cashback:after_buy_plus:horizont_text": {
    "elements": [
      {
        "type": "widget_group",
        "widget_group_id": "group_test",
        "display_rules": {
          "indent_rules_id": "default_indent_rules",
          "background_color_settings_id": "linear_gradient",
          "background_shape_settings": "default_shape_settings"
        }
      }
    ],
    "display_rules": {
      "indent_rules_id": "default_indent_rules",
      "background_color_settings_id": "linear_gradient",
      "background_shape_settings": "default_shape_settings"
    }
  },
  "level:widget:taxi:catching_up_cashback_text": {
      "elements": [
        {
          "type": "widget",
          "widget_id": "widget:taxi:catching_up_cashback_text",
          "display_rules": {
            "indent_rules_id": "default_indent_rules",
            "background_color_settings_id": "linear_gradient",
            "background_shape_settings": "default_shape_settings"
          }
        }
      ],
     "display_rules": {
       "indent_rules_id": "default_indent_rules",
       "background_color_settings_id": "linear_gradient",
        "background_shape_settings": "default_shape_settings"
    }
  },
  "level:widget:common:buy_plus": {
    "elements": [
      {
        "type": "widget",
        "widget_id": "widget:common:buy_plus",
        "display_rules": {
          "indent_rules_id": "default_indent_rules",
          "background_color_settings_id": "linear_gradient",
          "background_shape_settings": "default_shape_settings"
        }
      }
    ],
    "display_rules": {
      "indent_rules_id": "default_indent_rules",
      "background_color_settings_id": "linear_gradient",
      "background_shape_settings": "default_shape_settings"
    }
  },
  "level:widget:taxi:composite_payment": {
    "elements": [
      {
        "type": "widget",
        "widget_id": "widget:taxi:composite_payment",
        "display_rules": {
          "indent_rules_id": "default_indent_rules",
          "background_color_settings_id": "linear_gradient",
          "background_shape_settings": "default_shape_settings"
        }
      }
    ],
    "display_rules": {
      "indent_rules_id": "default_indent_rules",
      "background_color_settings_id": "linear_gradient",
      "background_shape_settings": "default_shape_settings"
    }
  },
  "level:widget:taxi:plus_burn": {
    "elements": [
      {
        "type": "widget",
        "widget_id": "widget:taxi:plus_burn",
        "display_rules": {
          "indent_rules_id": "default_indent_rules",
          "background_color_settings_id": "linear_gradient",
          "background_shape_settings": "default_shape_settings"
        }
      }
    ],
    "display_rules": {
      "indent_rules_id": "default_indent_rules",
      "background_color_settings_id": "linear_gradient",
      "background_shape_settings": "default_shape_settings"
    }
  }
}
)";

const std::string kPlaquesJson = R"(
{
  "__global__": {
    "plaque:global:buy_plus": {
      "widgets_level_id": [
        "level:widget:common:balance",
        "level:widget:common:buy_plus"
      ],
      "condition": {
        "screens": [
          "main"
        ],
        "tariffs": ["econom"],
        "selected_tariffs": [
          {
            "tariff": "econom",
            "vertical": "taxi"
          }
        ],
        "available_tariffs": [
          {
            "tariff": "econom",
            "vertical": "taxi"
          }
        ],
        "payment_methods": [
          "cash",
          "card"
        ]
      },
      "priority": 10,
      "params": {
        "show_after": 10,
        "close_after": 60
      },
      "visibility_requirements": {
        "has_plus": false
      },
      "display_rules": {
        "indent_rules_id": "default_indent_rules",
        "background_color_settings_id": "linear_gradient",
        "background_shape_settings": "default_shape_settings"
      },
      "visual_effects": [
        {
          "type": "CONFETTI",
          "trigger": "OPEN_PLAQUE"
        },
        {
          "type": "CONFETTI",
          "trigger": "SUCCESS_PURCHASE"
        },
        {
          "type": "CONFETTI",
          "trigger": "WIDGET",
          "widget": {
            "type": "CLICK",
            "widgets": ["1", "2"]
          }
        }
      ]
    }
  },
  "taxi": {
    "plaque:taxi:catching_up_cashback_no_positive_balance": {
      "widgets_level_id": [
        "level:widget:taxi:catching_up_cashback_text"
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
      "visibility_requirements": {
        "has_plus": false,
        "has_positive_balance": false
      },
      "display_rules": {
        "indent_rules_id": "default_indent_rules",
        "background_color_settings_id": "linear_gradient",
        "background_shape_settings": "default_shape_settings"
      }
    },
    "plaque:taxi:catching_up_cashback_has_positive_balance_success_purchase": {
      "widgets_level_id": [
        "level:widget:taxi:catching_up_cashback:after_buy_plus:horizont_text"
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
      "visibility_requirements": {
        "has_plus": true,
        "has_positive_balance": true
      },
      "display_rules": {
        "indent_rules_id": "default_indent_rules",
        "background_color_settings_id": "linear_gradient",
        "background_shape_settings": "default_shape_settings"
      }
    },
    "plaque:taxi:composite_payment": {
      "widgets_level_id": [
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
      "visibility_requirements": {
        "has_cashback_offer": true,
        "has_plus": true,
        "has_positive_balance": true
      },
      "display_rules": {
        "indent_rules_id": "default_indent_rules",
        "background_color_settings_id": "linear_gradient",
        "background_shape_settings": "default_shape_settings"
      }
    },
    "plaque:taxi:plus_burns": {
      "widgets_level_id": [
        "level:widget:common:balance",
        "level:widget:taxi:plus_burn"
      ],
      "condition": {
        "screens": [
          "summary"
        ]
      },
      "priority": 5,
      "params": {
        "show_after": 10,
        "close_after": 60
      },
      "visibility_requirements": {
        "has_plus": false,
        "has_positive_balance": true
      },
      "display_rules": {
        "indent_rules_id": "default_indent_rules",
        "background_color_settings_id": "linear_gradient",
        "background_shape_settings": "default_shape_settings"
      }
    }
  }
}
)";

const std::string kServiceId = "taxi";

}  // namespace

namespace {

dynamic_config::StorageMock PrepareTaxiConfig() {
  return dynamic_config::StorageMock{
      {taxi_config::PLUS_SWEET_HOME_PLAQUE_V2_WIDGETS,
       formats::json::FromString(kWidgetsJson)},
      {taxi_config::PLUS_SWEET_HOME_PLAQUES_V2_BY_SERVICE,
       formats::json::FromString(kPlaquesJson)},
      {taxi_config::PLUS_SWEET_HOME_WIDGETS_LEVEL,
       formats::json::FromString(kWidgetsLevelsJson)},
      {taxi_config::PLUS_SWEET_HOME_COLORS,
       formats::json::FromString(kColorsJson)},
      {taxi_config::PLUS_SWEET_HOME_INDENT_RULES,
       formats::json::FromString(kIndentRulesJson)},
      {taxi_config::PLUS_SWEET_HOME_WIDGET_GROUPS,
       formats::json::FromString(kWidgetGroupsJson)},
      {taxi_config::PLUS_SWEET_HOME_SHAPE_SETTINGS,
       formats::json::FromString(kShapeSettingsJson)}};
}

}  // namespace

TEST(TestConfigsPlaqueV2Repo, GetPlaques) {
  auto config_repo = PrepareTaxiConfig();
  auto config = config_repo.GetSnapshot();

  auto widgets = PrepareWidgets();
  auto levels = PrepareLevels(widgets);
  auto plaques = PreparePlaques(levels);

  auto repo = ConfigsPlaqueRepo(config);
  auto result = repo.GetPlaques(kServiceId);
  ASSERT_EQ(result.size(), 5);

  std::sort(result.begin(), result.end(), [](const auto& l, const auto& r) {
    return l.plaque_id < r.plaque_id;
  });

  {
    SCOPED_TRACE("Plaque: buy_plus");
    const auto& plaque = result[0];
    AssertPlaque(plaque, plaques["plaque:global:buy_plus"]);
  }

  {
    SCOPED_TRACE(
        "Plaque: catching_up_cashback_has_positive_balance_success_purchase");
    const auto& plaque = result[1];
    AssertPlaque(plaque, plaques["plaque:taxi:catching_up_cashback_has_"
                                 "positive_balance_success_purchase"]);
  }

  {
    SCOPED_TRACE("Plaque: catching_up_cashback_no_positive_balance");
    const auto& plaque = result[2];
    AssertPlaque(
        plaque,
        plaques["plaque:taxi:catching_up_cashback_no_positive_balance"]);
  }

  {
    SCOPED_TRACE("Plaque: composite_payment");
    const auto& plaque = result[3];
    AssertPlaque(plaque, plaques["plaque:taxi:composite_payment"]);
  }

  {
    SCOPED_TRACE("Plaque: plus_burns");
    const auto& plaque = result[4];
    AssertPlaque(plaque, plaques["plaque:taxi:plus_burns"]);
  }
}

}  // namespace plus_plaque::plaque::impl
