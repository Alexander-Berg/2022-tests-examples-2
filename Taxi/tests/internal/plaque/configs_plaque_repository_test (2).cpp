#include <testing/taxi_config.hpp>
#include <userver/formats/json.hpp>
#include <userver/utest/utest.hpp>

#include <taxi_config/variables/PLUS_SWEET_HOME_PLAQUES_BY_SERVICE.hpp>
#include <taxi_config/variables/PLUS_SWEET_HOME_PLAQUE_WIDGETS.hpp>

#include "internal/plaque/impl/configs_plaque_repository.hpp"

#include "tests/internal/models_test.hpp"
#include "tests/internal/plaque/models_test.hpp"

namespace sweet_home::plaque::impl {

namespace {
const std::string kWidgetsJson = R"(
{
  "widget:common:balance_without_text": {
    "type": "BALANCE",
    "balance": {}
  },
  "widget:taxi:catching_up_cashback_text": {
     "type": "TEXT",
     "text": {
        "text_key": "sweet_home.plaque.widgets.catching_up_cashback.text",
        "attributed_text_key": "sweet_home.plaque.widgets.catching_up_cashback.text"
     }
  },
  "widget:taxi:catching_up_cashback:after_buy_plus:horizont_text": {
     "type": "HORIZONT_TEXT",
     "horizont_text": {
        "text_left_key": "sweet_home.plaque.widgets.catching_up_cashback.after_buy_plus.text_left",
        "text_right_key": "sweet_home.plaque.widgets.catching_up_cashback.after_buy_plus.text_right"
     }
  },
  "widget:common:buy_plus": {
    "type": "BUTTON",
    "button": {
      "text_key": "sweet_home.plaque.widgets.buy_plus.text"
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
    }
  }
}
)";

const std::string kPlaquesJson = R"(
{
  "__global__": {
    "plaque:global:buy_plus": {
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
      },
      "visibility_requirements": {
        "has_plus": false
      }
    }
  },
  "taxi": {
    "plaque:taxi:catching_up_cashback_no_positive_balance": {
      "layout": "VERTICAL",
      "widgets": [
        "widget:taxi:catching_up_cashback_text"
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
      }
    },
    "plaque:taxi:catching_up_cashback_has_positive_balance_success_purchase": {
      "layout": "VERTICAL",
      "widgets": [
        "widget:taxi:catching_up_cashback:after_buy_plus:horizont_text"
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
      }
    },
    "plaque:taxi:composite_payment": {
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
      },
      "visibility_requirements": {
        "has_cashback_offer": true,
        "has_plus": true,
        "has_positive_balance": true
      }
    },
    "plaque:taxi:plus_burns": {
      "layout": "VERTICAL",
      "widgets": [
        "widget:common:balance_without_text",
        "widget:taxi:plus_burn"
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
      {taxi_config::PLUS_SWEET_HOME_PLAQUE_WIDGETS,
       formats::json::FromString(kWidgetsJson)},
      {taxi_config::PLUS_SWEET_HOME_PLAQUES_BY_SERVICE,
       formats::json::FromString(kPlaquesJson)},
  };
}

}  // namespace

TEST(TestConfigsPlaqueRepo, GetPlaques) {
  auto config_repo = PrepareTaxiConfig();
  auto config = config_repo.GetSnapshot();

  auto widgets = PrepareWidgets();
  auto plaques = PreparePlaques(widgets);

  auto repo = ConfigsPlaqueRepo(config);
  auto result = repo.GetPlaques(kServiceId);
  ASSERT_EQ(result.size(), 5);

  {
    SCOPED_TRACE("Plaque: buy_plus");
    const auto& plaque = result[0];
    AssertPlaque(plaque, plaques["plaque:global:buy_plus"]);
  }

  {
    SCOPED_TRACE("Plaque: catching_up_cashback_no_positive_balance");
    const auto& plaque = result[1];
    AssertPlaque(
        plaque,
        plaques["plaque:taxi:catching_up_cashback_no_positive_balance"]);
  }

  {
    SCOPED_TRACE("Plaque: plus_burns");
    const auto& plaque = result[2];
    AssertPlaque(plaque, plaques["plaque:taxi:plus_burns"]);
  }

  {
    SCOPED_TRACE(
        "Plaque: catching_up_cashback_has_positive_balance_success_purchase");
    const auto& plaque = result[3];
    AssertPlaque(plaque, plaques["plaque:taxi:catching_up_cashback_has_"
                                 "positive_balance_success_purchase"]);
  }

  {
    SCOPED_TRACE("Plaque: composite_payment");
    const auto& plaque = result[4];
    AssertPlaque(plaque, plaques["plaque:taxi:composite_payment"]);
  }
}

}  // namespace sweet_home::plaque::impl
