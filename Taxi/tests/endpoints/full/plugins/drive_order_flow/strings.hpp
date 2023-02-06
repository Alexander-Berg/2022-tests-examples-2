#pragma once

#include <string>

namespace routestats::plugins::drive_order_flow::test::strings {

const std::string kNonFullOffersResponse = R"(
  {
    "class": "",
    "selector": {
      "is_hidden": true,
      "icon": {
        "tag": "car_icon_kaptur"
      },
      "image": {
        "url": "https://tc.mobile.yandex.net/foobar/kaptur_4x"
      }
    },
    "drive_extra": {
      "layers_context": {
        "type": "drive_fixpoint_offers",
        "src": [
          35.5,
          55.5
        ],
        "dst": [
          35.6,
          55.7
        ],
        "destination_name": "",
        "offer_count_limit": 0,
        "preferred_car_number": "т577нх799",
        "previous_offer_ids": [
          "3e29f7f7-8a7d26c2-4359f132-d6e0ee72"
        ],
        "summary_tariff_class": "drive",
        "size_hint": 500
      },
      "offer_ids": [
        "3e29f7f7-8a7d26c2-4359f132-d6e0ee72"
      ],
      "offer_id": "3e29f7f7-8a7d26c2-4359f132-d6e0ee72",
      "car_number": "т577нх799"
    }
  }
)";

const std::string kNonFullOffersResponseNoReg = R"(
  {
    "class": "",
    "selector": {
      "is_hidden": true,
      "icon": {
        "tag": "car_icon_kaptur"
      },
      "image": {
        "url": "https://tc.mobile.yandex.net/foobar/kaptur_4x"
      }
    },
    "drive_extra": {
      "layers_context": {
        "type": "drive_fixpoint_offers",
        "src": [
          35.5,
          55.5
        ],
        "dst": [
          35.6,
          55.7
        ],
        "destination_name": "",
        "offer_count_limit": 0,
        "preferred_car_number": "т577нх799",
        "previous_offer_ids": [],
        "summary_tariff_class": "drive",
        "size_hint": 500,
        "drive_response": {
          "is_registred": false,
          "is_service_available": true,
          "offers": [
            {
              "offer_type": "fix_point",
              "number": "т577нх799",
              "deeplink": "yandexdrive://cars/т577нх799?offer_id=3e29f7f7-8a7d26c2-4359f132-d6e0ee72",
              "riding_duration": 516,
              "localized_riding_duration": "8 мин",
              "price_undiscounted": 10000,
              "localized_free_reservation_duration": "16 мин",
              "walking_duration": 540,
              "localized_walking_duration": "9 мин",
              "localized_price": "74 ₽",
              "price": 7400,
              "button_text": "Забронировать",
              "cashback_prediction": 900
            }
          ],
          "cars": [
            {
              "number": "т577нх799",
              "location": {
                "lon": 49.23548301,
                "lat": 55.77193853,
                "course": 358
              },
              "view": 0,
              "telematics": {
                "fuel_level": 71
              },
              "model_id": "renault_kaptur"
            }
          ],
          "views": [
            {
              "code": "renault_kaptur",
              "name": "Renault Kaptur",
              "short_name": "Kaptur",
              "image_map_url_2x": "https://carsharing.s3.yandex.net/drive/car-models/renault_kaptur/map-2x.png?r=3",
              "image_map_url_3x": "https://carsharing.s3.yandex.net/drive/car-models/renault_kaptur/map-3x.png?r=3",
              "image_pin_url_2x": "https://carsharing.s3.yandex.net/autoupload/renault_kaptur/1581340232/2white-map-pin__feb2020@2x.png",
              "image_pin_url_3x": "https://carsharing.s3.yandex.net/autoupload/renault_kaptur/1581340232/2white-map-pin__feb2020@3x.png",
              "image_large_url": "https://carsharing.s3.yandex.net/drive/car-models/renault_kaptur/renault-kaptur-side-2-kaz_large.png",
              "meta": {
                "yandexgo_image_4x": "https://tc.mobile.yandex.net/foobar/kaptur_4x"
              }
            }
          ]
        }
      },
      "offer_ids": [],
      "offer_id": "",
      "car_number": "т577нх799"
    }
  }
)";

const std::string kFullOffersResponse = R"(
  {
    "class": "",
    "selector": {
      "is_hidden": true,
      "icon": {
        "tag": "car_icon_kaptur"
      },
      "image": {
        "url": "https://tc.mobile.yandex.net/foobar/kaptur_4x"
      }
    },
    "drive_extra": {
      "layers_context": {
        "type": "drive_fixpoint_offers",
        "src": [
          35.5,
          55.5
        ],
        "dst": [
          35.6,
          55.7
        ],
        "destination_name": "",
        "offer_count_limit": 0,
        "preferred_car_number": "т577нх799",
        "previous_offer_ids": [
          "3e29f7f7-8a7d26c2-4359f132-d6e0ee72"
        ],
        "summary_tariff_class": "drive",
        "size_hint": 500
      },
      "offers": [
        {
          "offer_id": "3e29f7f7-8a7d26c2-4359f132-d6e0ee72",
          "type": "summary",
          "base_service_level_class": "drive",
          "layers_extra": {
            "car_number": "т577нх799",
            "layers_object_id": "drive__т577нх799"
          },
          "service_level_override": {
            "class": "drive",
            "name": "Kaptur",
            "brandings": [
              {
                "type": "cashback",
                "value": "9",
                "title": "summary.drive.cashback.title##ru",
                "tooltip": {
                  "text": "summary.drive.cashback.tooltip.text##ru"
                }
              }
            ],
            "selector": {
              "icon": {
                "tag": "car_icon_kaptur"
              },
              "image": {
                "url": "https://tc.mobile.yandex.net/foobar/kaptur_4x"
              }
            },
            "description_parts": {
              "prefix": "",
              "suffix": "",
              "value": "74 $SIGN$$CURRENCY$",
              "value_undiscounted":"100 $SIGN$$CURRENCY$"
            },
            "estimated_waiting": {
              "seconds": 540,
              "message": "summary.drive.estimated_waiting.message##ru"
            },
            "description": "summary.drive.description##ru",
            "title": "summary.drive.button.title##ru",
            "subtitle": "summary.drive.button.subtitle##ru"
          }
        }
      ]
    }
  }
)";

const std::string kFullOffersResponseNoReg = R"(
  {
    "class": "",
    "selector": {
      "is_hidden": true,
      "icon": {
        "tag": "car_icon_kaptur"
      },
      "image": {
        "url": "https://tc.mobile.yandex.net/foobar/kaptur_4x"
      }
    },
    "drive_extra": {
      "layers_context": {
        "type": "drive_fixpoint_offers",
        "src": [
          35.5,
          55.5
        ],
        "dst": [
          35.6,
          55.7
        ],
        "destination_name": "",
        "offer_count_limit": 0,
        "preferred_car_number": "т577нх799",
        "previous_offer_ids": [
        ],
        "summary_tariff_class": "drive",
        "size_hint": 500,
        "drive_response": {
          "is_registred": false,
          "is_service_available": true,
          "offers": [
            {
              "offer_type": "fix_point",
              "number": "т577нх799",
              "deeplink": "yandexdrive://cars/т577нх799?offer_id=3e29f7f7-8a7d26c2-4359f132-d6e0ee72",
              "riding_duration": 516,
              "localized_riding_duration": "8 мин",
              "price_undiscounted": 10000,
              "localized_free_reservation_duration": "16 мин",
              "walking_duration": 540,
              "localized_walking_duration": "9 мин",
              "localized_price": "74 ₽",
              "price": 7400,
              "button_text": "Забронировать",
              "cashback_prediction": 900
            }
          ],
          "cars": [
            {
              "number": "т577нх799",
              "location": {
                "lon": 49.23548301,
                "lat": 55.77193853,
                "course": 358
              },
              "view": 0,
              "telematics": {
                "fuel_level": 71
              },
              "model_id": "renault_kaptur"
            }
          ],
          "views": [
            {
              "code": "renault_kaptur",
              "name": "Renault Kaptur",
              "short_name": "Kaptur",
              "image_map_url_2x": "https://carsharing.s3.yandex.net/drive/car-models/renault_kaptur/map-2x.png?r=3",
              "image_map_url_3x": "https://carsharing.s3.yandex.net/drive/car-models/renault_kaptur/map-3x.png?r=3",
              "image_pin_url_2x": "https://carsharing.s3.yandex.net/autoupload/renault_kaptur/1581340232/2white-map-pin__feb2020@2x.png",
              "image_pin_url_3x": "https://carsharing.s3.yandex.net/autoupload/renault_kaptur/1581340232/2white-map-pin__feb2020@3x.png",
              "image_large_url": "https://carsharing.s3.yandex.net/drive/car-models/renault_kaptur/renault-kaptur-side-2-kaz_large.png",
              "meta": {
                "yandexgo_image_4x": "https://tc.mobile.yandex.net/foobar/kaptur_4x"
              }
            }
          ]
        }
      },
      "offers": [
        {
          "offer_id": "",
          "type": "summary",
          "base_service_level_class": "drive",
          "layers_extra": {
            "car_number": "т577нх799",
            "layers_object_id": "drive__т577нх799"
          },
          "service_level_override": {
            "class": "drive",
            "name": "Kaptur",
            "brandings": [
              {
                "type": "cashback",
                "value": "9",
                "title": "summary.drive.cashback.title##ru",
                "tooltip": {
                  "text": "summary.drive.cashback.tooltip.text##ru"
                }
              }
            ],
            "selector": {
              "icon": {
                "tag": "car_icon_kaptur"
              },
              "image": {
                "url": "https://tc.mobile.yandex.net/foobar/kaptur_4x"
              }
            },
            "description_parts": {
              "prefix": "",
              "suffix": "",
              "value": "74 $SIGN$$CURRENCY$",
              "value_undiscounted":"100 $SIGN$$CURRENCY$"
            },
            "estimated_waiting": {
              "seconds": 540,
              "message": "summary.drive.estimated_waiting.message##ru"
            },
            "description": "summary.drive.description##ru",
            "title": "summary.drive.button.title##ru",
            "subtitle": "summary.drive.button.subtitle##ru"
          }
        }
      ]
    }
  }
)";

}  // namespace routestats::plugins::drive_order_flow::test::strings
