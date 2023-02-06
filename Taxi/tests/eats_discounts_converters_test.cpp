#include <gtest/gtest.h>
#include <taxi_config/variables/EATS_RESTAPP_PROMO_FREE_DELIVERY_CREATE_SETTINGS.hpp>
#include <testing/taxi_config.hpp>

#include <userver/utils/from_string.hpp>

#include <clients/eats-discounts/client.hpp>
#include <models/place_promo.hpp>
#include <types/discount_data.hpp>
#include <utils/discounts/eats_discounts_converters.hpp>
#include <utils/schedule_converter.hpp>

TEST(GetCreateDiscountsData, IncorrectPromoType) {
  const auto config = dynamic_config::GetDefaultSnapshot();
  eats_restapp_promo::models::PromoData promo_data_gift{};
  promo_data_gift.promo_type = eats_restapp_promo::models::PromoType::kGift;
  ASSERT_ANY_THROW(eats_restapp_promo::utils::discounts::GetCreateDiscountsData(
      promo_data_gift, config,
      experiments3::eats_restapp_promo_settings::Value{}));

  eats_restapp_promo::models::PromoData promo_data_discount{};
  promo_data_discount.promo_type =
      eats_restapp_promo::models::PromoType::kDiscount;
  ASSERT_ANY_THROW(eats_restapp_promo::utils::discounts::GetCreateDiscountsData(
      promo_data_discount, config,
      experiments3::eats_restapp_promo_settings::Value{}));

  eats_restapp_promo::models::PromoData promo_data_one_plus_one{};
  promo_data_one_plus_one.promo_type =
      eats_restapp_promo::models::PromoType::kOnePlusOne;
  ASSERT_ANY_THROW(eats_restapp_promo::utils::discounts::GetCreateDiscountsData(
      promo_data_one_plus_one, config,
      experiments3::eats_restapp_promo_settings::Value{}));
}

TEST(GetCreateDiscountsData, PlusPromoWithoutCashback) {
  const auto config = dynamic_config::GetDefaultSnapshot();
  eats_restapp_promo::models::PromoData promo_plus_happy_hours{};
  promo_plus_happy_hours.promo_type =
      eats_restapp_promo::models::PromoType::kPlusHappyHours;
  ASSERT_ANY_THROW(eats_restapp_promo::utils::discounts::GetCreateDiscountsData(
      promo_plus_happy_hours, config,
      experiments3::eats_restapp_promo_settings::Value{}));

  eats_restapp_promo::models::PromoData promo_plus_first_orders{};
  promo_plus_first_orders.promo_type =
      eats_restapp_promo::models::PromoType::kPlusFirstOrders;
  ASSERT_ANY_THROW(eats_restapp_promo::utils::discounts::GetCreateDiscountsData(
      promo_plus_first_orders, config,
      experiments3::eats_restapp_promo_settings::Value{}));
}

TEST(GetCreateDiscountsData, PlusHappyHours) {
  clients::eats_discounts::PartnersDiscountCreateData expected_item =
      formats::json::FromString(R"({
"data": {
  "discount": {
    "discount_meta": {
      "name": "plus_happy_hours"
    },
    "name": "plus_happy_hours",
    "values_with_schedules": [
      {
        "cashback_value": {
          "menu_value": {
            "value": "55.500000",
            "value_type": "fraction"
          }
        },
        "schedule": {
          "intervals": [
            {
              "day": [
                1
              ],
              "exclude": false
            },
            {
              "exclude": false,
              "daytime": [
                {
                  "from": "00:00:00",
                  "to": "02:00:00"
                }
              ]
            }
          ],
          "timezone": "LOCAL"
        }
      }
    ]
  },
  "hierarchy_name": "place_cashback"
},
"rules": [
  {
    "condition_name": "place",
    "values": [
      1,
      2
    ]
  },
  {
    "condition_name": "active_period",
    "values": [
      {
        "end": "2021-10-31T21:00:00+00:00",
        "is_end_utc": true,
        "is_start_utc": true,
        "start": "2021-10-29T21:00:00+00:00"
      }
    ]
  },
  {
    "condition_name": "has_yaplus",
    "values": [
      1
    ]
  },
  {
    "condition_name": "check",
    "values": [
      {
        "end": "1000000",
        "start": "1234",
        "type": "double_range"
      }
    ]
  }
]
})")
          .As<clients::eats_discounts::PartnersDiscountCreateData>();

  eats_restapp_promo::models::PromoData promo_plus_happy_hours{};
  promo_plus_happy_hours.promo_type =
      eats_restapp_promo::models::PromoType::kPlusHappyHours;
  promo_plus_happy_hours.place_ids = {eats_restapp_promo::models::PlaceId{'1'},
                                      eats_restapp_promo::models::PlaceId{'2'}};

  promo_plus_happy_hours.starts =
      utils::datetime::Stringtime("2021-10-29T21:00:00Z", "UTC");
  promo_plus_happy_hours.ends =
      utils::datetime::Stringtime("2021-10-31T21:00:00Z", "UTC");

  eats_restapp_promo::models::PromoRequirement requirement;
  requirement.min_order_price = 1234;
  promo_plus_happy_hours.requirements = {requirement};

  eats_restapp_promo::models::PromoBonus bonus;
  bonus.cashback = {55.5};
  promo_plus_happy_hours.bonuses = {bonus};

  std::vector<eats_restapp_promo::models::PromoSchedule> schedule;
  schedule = {{1, 0, 120}};
  promo_plus_happy_hours.schedule = schedule;
  const auto config = dynamic_config::GetDefaultSnapshot();

  const auto converted =
      eats_restapp_promo::utils::discounts::GetCreateDiscountsData(
          promo_plus_happy_hours, config,
          experiments3::eats_restapp_promo_settings::Value{});

  ASSERT_EQ(converted.size(), 1);

  const auto converted_data =
      std::get<clients::eats_discounts::PlaceCashbackData>(
          converted.front().data.AsVariant());
  const auto expected_item_data =
      std::get<clients::eats_discounts::PlaceCashbackData>(
          expected_item.data.AsVariant());

  ASSERT_EQ(converted.front().rules, expected_item.rules);
  ASSERT_EQ(converted_data.hierarchy_name, expected_item_data.hierarchy_name);
  ASSERT_EQ(converted_data.discount.name, expected_item_data.discount.name);
  ASSERT_EQ(converted_data.discount.discount_meta.name,
            expected_item_data.discount.discount_meta.name);
  ASSERT_EQ(converted_data.discount.values_with_schedules.size(), 1);

  const auto converted_cashback = std::get<
      clients::eats_discounts::libraries::discounts::FractionValueWithMaximum>(
      converted_data.discount.values_with_schedules.front()
          .cashback_value.menu_value.AsVariant());
  const auto expected_item_cashback = std::get<
      clients::eats_discounts::libraries::discounts::FractionValueWithMaximum>(
      expected_item_data.discount.values_with_schedules.front()
          .cashback_value.menu_value.AsVariant());

  ASSERT_EQ(utils::FromString<double>(converted_cashback.value),
            utils::FromString<double>(expected_item_cashback.value));

  const auto converted_json_schedule =
      Serialize(converted_data.discount.values_with_schedules.front().schedule,
                formats::serialize::To<formats::json::Value>{});
  const auto expected_json_schedule = Serialize(
      expected_item_data.discount.values_with_schedules.front().schedule,
      formats::serialize::To<formats::json::Value>{});
  ASSERT_EQ(converted_json_schedule, expected_json_schedule);
}

TEST(GetCreateDiscountsData, PlusFirstOrders) {
  clients::eats_discounts::PartnersDiscountCreateData expected_item1 =
      formats::json::FromString(R"({
"data": {
  "discount": {
    "discount_meta": {
      "name": "plus_first_orders"
    },
    "name": "plus_first_orders",
    "values_with_schedules": [
      {
        "cashback_value": {
          "menu_value": {
            "value": "50",
            "value_type": "fraction"
          }
        },
        "schedule": {
          "intervals": [
            {
              "day": [
                1,2,3,4,5,6,7
              ],
              "exclude": false
            }
          ],
          "timezone": "LOCAL"
        }
      }
    ]
  },
  "hierarchy_name": "place_cashback"
},
"rules": [
  {
    "condition_name": "place",
    "values": [
      1,
      2
    ]
  },
  {
    "condition_name": "active_period",
    "values": [
      {
        "end": "2021-10-31T21:00:00+00:00",
        "is_end_utc": true,
        "is_start_utc": true,
        "start": "2021-10-29T21:00:00+00:00"
      }
    ]
  },
  {
    "condition_name": "has_yaplus",
    "values": [
      1
    ]
  },
  {
    "condition_name": "place_orders_count",
    "values": [
      {
        "start": 0,
        "end": 1
      }
    ]
  },
  {
    "condition_name": "check",
    "values": [
      {
        "end": "50000",
        "start": "1234",
        "type": "double_range"
      }
    ]
  }
]
})")
          .As<clients::eats_discounts::PartnersDiscountCreateData>();

  clients::eats_discounts::PartnersDiscountCreateData expected_item2 =
      formats::json::FromString(R"({
"data": {
  "discount": {
    "discount_meta": {
      "name": "plus_first_orders"
    },
    "name": "plus_first_orders",
    "values_with_schedules": [
      {
        "cashback_value": {
          "menu_value": {
            "value": "12.500000",
            "value_type": "fraction"
          }
        },
        "schedule": {
          "intervals": [
            {
              "day": [
                1,2,3,4,5,6,7
              ],
              "exclude": false
            }
          ],
          "timezone": "LOCAL"
        }
      }
    ]
  },
  "hierarchy_name": "place_cashback"
},
"rules": [
  {
    "condition_name": "place",
    "values": [
      1,
      2
    ]
  },
  {
    "condition_name": "active_period",
    "values": [
      {
        "end": "2021-10-31T21:00:00+00:00",
        "is_end_utc": true,
        "is_start_utc": true,
        "start": "2021-10-29T21:00:00+00:00"
      }
    ]
  },
  {
    "condition_name": "has_yaplus",
    "values": [
      1
    ]
  },
  {
    "condition_name": "place_orders_count",
    "values": [
      {
        "start": 1,
        "end": 2
      }
    ]
  },
  {
    "condition_name": "check",
    "values": [
      {
        "end": "50000",
        "start": "1234",
        "type": "double_range"
      }
    ]
  }
]
})")
          .As<clients::eats_discounts::PartnersDiscountCreateData>();

  auto promo_settings =
      formats::json::FromString(R"(
{
  "plus_first_orders": {
    "type": "plus_first_orders",
    "is_new": true,
    "enabled": true,
    "can_edit": false,
    "can_stop": true,
    "icon_url": "invalid.invalid",
    "can_pause": false,
    "can_create": true,
    "configuration": {
      "type": "plus_first_orders",
      "max_order_price": {
        "minimum": 0.0,
        "maximum": 50000.0
      },
      "cashback": {
        "maximum": 50,
        "minimum": 20
      }
    },
    "is_multiple_places_allowed": true,
    "hierarchy_name": "place_cashback"
  }
}
  )")
          .As<experiments3::eats_restapp_promo_settings::Value>();

  eats_restapp_promo::models::PromoData promo_plus_first_orders{};
  promo_plus_first_orders.promo_type =
      eats_restapp_promo::models::PromoType::kPlusFirstOrders;
  promo_plus_first_orders.place_ids = {
      eats_restapp_promo::models::PlaceId{'1'},
      eats_restapp_promo::models::PlaceId{'2'}};

  promo_plus_first_orders.starts =
      utils::datetime::Stringtime("2021-10-29T21:00:00Z", "UTC");
  promo_plus_first_orders.ends =
      utils::datetime::Stringtime("2021-10-31T21:00:00Z", "UTC");

  eats_restapp_promo::models::PromoRequirement requirement;
  requirement.min_order_price = 1234;
  promo_plus_first_orders.requirements = {requirement};

  eats_restapp_promo::models::PromoBonus bonus;
  bonus.cashback = {50, 12.5};
  promo_plus_first_orders.bonuses = {bonus};

  const auto config = dynamic_config::GetDefaultSnapshot();
  const auto converted =
      eats_restapp_promo::utils::discounts::GetCreateDiscountsData(
          promo_plus_first_orders, config, promo_settings);

  ASSERT_EQ(converted.size(), 2);

  //// FIRST
  auto converted_data = std::get<clients::eats_discounts::PlaceCashbackData>(
      converted[0].data.AsVariant());
  auto expected_item_data =
      std::get<clients::eats_discounts::PlaceCashbackData>(
          expected_item1.data.AsVariant());

  ASSERT_EQ(converted[0].rules, expected_item1.rules);
  ASSERT_EQ(converted_data.hierarchy_name, expected_item_data.hierarchy_name);
  ASSERT_EQ(converted_data.discount.name, expected_item_data.discount.name);
  ASSERT_EQ(converted_data.discount.discount_meta.name,
            expected_item_data.discount.discount_meta.name);
  ASSERT_EQ(converted_data.discount.values_with_schedules.size(), 1);

  auto converted_cashback = std::get<
      clients::eats_discounts::libraries::discounts::FractionValueWithMaximum>(
      converted_data.discount.values_with_schedules.front()
          .cashback_value.menu_value.AsVariant());
  auto expected_item_cashback = std::get<
      clients::eats_discounts::libraries::discounts::FractionValueWithMaximum>(
      expected_item_data.discount.values_with_schedules.front()
          .cashback_value.menu_value.AsVariant());

  ASSERT_EQ(utils::FromString<double>(converted_cashback.value),
            utils::FromString<double>(expected_item_cashback.value));

  auto converted_json_schedule =
      Serialize(converted_data.discount.values_with_schedules.front().schedule,
                formats::serialize::To<formats::json::Value>{});
  auto expected_json_schedule = Serialize(
      expected_item_data.discount.values_with_schedules.front().schedule,
      formats::serialize::To<formats::json::Value>{});
  ASSERT_EQ(converted_json_schedule, expected_json_schedule);

  //// SECOND
  converted_data = std::get<clients::eats_discounts::PlaceCashbackData>(
      converted[1].data.AsVariant());
  expected_item_data = std::get<clients::eats_discounts::PlaceCashbackData>(
      expected_item2.data.AsVariant());

  ASSERT_EQ(converted[1].rules, expected_item2.rules);
  ASSERT_EQ(converted_data.hierarchy_name, expected_item_data.hierarchy_name);
  ASSERT_EQ(converted_data.discount.name, expected_item_data.discount.name);
  ASSERT_EQ(converted_data.discount.discount_meta.name,
            expected_item_data.discount.discount_meta.name);
  ASSERT_EQ(converted_data.discount.values_with_schedules.size(), 1);

  converted_cashback = std::get<
      clients::eats_discounts::libraries::discounts::FractionValueWithMaximum>(
      converted_data.discount.values_with_schedules.front()
          .cashback_value.menu_value.AsVariant());
  expected_item_cashback = std::get<
      clients::eats_discounts::libraries::discounts::FractionValueWithMaximum>(
      expected_item_data.discount.values_with_schedules.front()
          .cashback_value.menu_value.AsVariant());

  ASSERT_EQ(utils::FromString<double>(converted_cashback.value),
            utils::FromString<double>(expected_item_cashback.value));

  converted_json_schedule =
      Serialize(converted_data.discount.values_with_schedules.front().schedule,
                formats::serialize::To<formats::json::Value>{});
  expected_json_schedule = Serialize(
      expected_item_data.discount.values_with_schedules.front().schedule,
      formats::serialize::To<formats::json::Value>{});
  ASSERT_EQ(converted_json_schedule, expected_json_schedule);
}

TEST(GetCreateDiscountsData, FreeDelivery) {
  clients::eats_discounts::PartnersDiscountCreateData expected_item1 =
      formats::json::FromString(R"(
{
  "rules": [
    {
      "condition_name": "place",
      "values": [
        1,
        2
      ]
    },
    {
      "condition_name": "active_period",
      "values": [
        {
          "start": "2021-10-29T21:00:00+00:00",
          "is_start_utc": true,
          "end": "2021-10-31T21:00:00+00:00",
          "is_end_utc": true
        }
      ]
    },
    {
      "condition_name": "check",
      "values": [
        {
          "type": "double_range",
          "start": "300",
          "end": "1000000"
        }
      ]
    },
    {
      "condition_name": "brand_orders_count",
      "values": [
        {
          "start": 0,
          "end": 1
        }
      ]
    },
    {
      "condition_name": "delivery_method",
      "values": [
        "pedestrian"
      ]
    }
  ],
  "data": {
    "hierarchy_name": "place_delivery_discounts",
    "discount": {
      "name": "free_delivery",
      "values_with_schedules": [
        {
          "schedule": {
            "timezone": "LOCAL",
            "intervals": [
              {
                "exclude": false,
                "day": [
                  1,
                  2,
                  3,
                  4,
                  5,
                  6,
                  7
                ]
              }
            ]
          },
          "money_value": {
            "menu_value": {
              "value_type": "fraction",
              "value": "100"
            }
          }
        }
      ],
      "discount_meta": {
        "promo": {
          "name": "Бесплатная доставка от 300 руб.",
          "description": "На первый заказ от 300₽ в этом ресторане.",
          "picture_uri": "picture_uri"
        }
      }
    }
  }
}
)")
          .As<clients::eats_discounts::PartnersDiscountCreateData>();

  clients::eats_discounts::PartnersDiscountCreateData expected_item2 =
      formats::json::FromString(R"(
{
  "rules": [
    {
      "condition_name": "place",
      "values": [
        1,
        2
      ]
    },
    {
      "condition_name": "active_period",
      "values": [
        {
          "start": "2021-10-29T21:00:00+00:00",
          "is_start_utc": true,
          "end": "2021-10-31T21:00:00+00:00",
          "is_end_utc": true
        }
      ]
    },
    {
      "condition_name": "check",
      "values": [
        {
          "type": "double_range",
          "start": "300",
          "end": "10000"
        }
      ]
    },
    {
      "condition_name": "brand_orders_count",
      "values": [
        {
          "start": 0,
          "end": 1
        }
      ]
    },
    {
      "condition_name": "delivery_method",
      "values": [
        "pedestrian"
      ]
    }
  ],
  "data": {
    "hierarchy_name": "place_delivery_discounts",
    "discount": {
      "name": "free_delivery",
      "values_with_schedules": [
        {
          "schedule": {
            "timezone": "LOCAL",
            "intervals": [
              {
                "exclude": false,
                "day": [
                  1,
                  2,
                  3,
                  4,
                  5,
                  6,
                  7
                ]
              }
            ]
          },
          "money_value": {
            "menu_value": {
              "value_type": "fraction",
              "value": "100"
            }
          }
        }
      ],
      "discount_meta": {
        "promo": {
          "name": "Бесплатная доставка от 300 руб.",
          "description": "На первый заказ от 300₽ в этом ресторане.",
          "picture_uri": "picture_uri"
        }
      }
    }
  }
}
)")
          .As<clients::eats_discounts::PartnersDiscountCreateData>();

  auto promo_settings1 =
      formats::json::FromString(R"(
{
  "free_delivery": {
    "type": "free_delivery",
    "is_new": true,
    "enabled": false,
    "can_edit": false,
    "can_stop": true,
    "icon_url": "invalid.invalid",
    "can_pause": false,
    "can_create": true,
    "configuration": {
      "type": "free_delivery",
      "max_order_price": {
        "minimum": 0.0,
        "maximum": 10000.0
      }
    },
    "is_multiple_places_allowed": true,
    "hierarchy_name": "place_delivery_discounts"
  }
}
  )")
          .As<experiments3::eats_restapp_promo_settings::Value>();

  auto promo_settings2 =
      formats::json::FromString(R"(
{
  "free_delivery": {
    "type": "free_delivery",
    "is_new": true,
    "enabled": true,
    "can_edit": false,
    "can_stop": true,
    "icon_url": "invalid.invalid",
    "can_pause": false,
    "can_create": true,
    "configuration": {
      "type": "free_delivery",
      "max_order_price": {
        "minimum": 0.0,
        "maximum": 10000.0
      }
    },
    "is_multiple_places_allowed": true,
    "hierarchy_name": "place_delivery_discounts"
  }
}
  )")
          .As<experiments3::eats_restapp_promo_settings::Value>();

  eats_restapp_promo::models::PromoData promo_free_delivery{};
  promo_free_delivery.promo_type =
      eats_restapp_promo::models::PromoType::kFreeDelivery;
  promo_free_delivery.place_ids = {eats_restapp_promo::models::PlaceId{'1'},
                                   eats_restapp_promo::models::PlaceId{'2'}};

  promo_free_delivery.starts =
      utils::datetime::Stringtime("2021-10-29T21:00:00Z", "UTC");
  promo_free_delivery.ends =
      utils::datetime::Stringtime("2021-10-31T21:00:00Z", "UTC");

  eats_restapp_promo::models::PromoRequirement requirement;
  requirement.min_order_price = 300;
  promo_free_delivery.requirements = {requirement};

  const auto config = dynamic_config::GetDefaultSnapshot();

  {
    const auto converted =
        eats_restapp_promo::utils::discounts::GetCreateDiscountsData(
            promo_free_delivery, config, promo_settings1);

    ASSERT_EQ(converted.size(), 1);

    auto converted_data =
        std::get<clients::eats_discounts::PlaceDeliveryDiscountData>(
            converted[0].data.AsVariant());
    auto expected_item_data =
        std::get<clients::eats_discounts::PlaceDeliveryDiscountData>(
            expected_item1.data.AsVariant());

    ASSERT_EQ(converted[0].rules, expected_item1.rules);
    ASSERT_EQ(converted_data.hierarchy_name, expected_item_data.hierarchy_name);
    ASSERT_EQ(converted_data.discount.name, expected_item_data.discount.name);
    ASSERT_EQ(converted_data.discount.values_with_schedules.size(), 1);

    auto converted_discounts_value =
        std::get<clients::eats_discounts::libraries::discounts::
                     FractionValueWithMaximum>(
            converted_data.discount.values_with_schedules.front()
                .money_value.menu_value.AsVariant());
    auto expected_discounts_value =
        std::get<clients::eats_discounts::libraries::discounts::
                     FractionValueWithMaximum>(
            expected_item_data.discount.values_with_schedules.front()
                .money_value.menu_value.AsVariant());

    ASSERT_EQ(utils::FromString<double>(converted_discounts_value.value),
              utils::FromString<double>(expected_discounts_value.value));

    auto converted_json_schedule = Serialize(
        converted_data.discount.values_with_schedules.front().schedule,
        formats::serialize::To<formats::json::Value>{});
    auto expected_json_schedule = Serialize(
        expected_item_data.discount.values_with_schedules.front().schedule,
        formats::serialize::To<formats::json::Value>{});
    ASSERT_EQ(converted_json_schedule, expected_json_schedule);
  }

  {
    const auto converted =
        eats_restapp_promo::utils::discounts::GetCreateDiscountsData(
            promo_free_delivery, config, promo_settings2);

    ASSERT_EQ(converted.size(), 1);

    auto converted_data =
        std::get<clients::eats_discounts::PlaceDeliveryDiscountData>(
            converted[0].data.AsVariant());
    auto expected_item_data =
        std::get<clients::eats_discounts::PlaceDeliveryDiscountData>(
            expected_item2.data.AsVariant());

    ASSERT_EQ(converted[0].rules, expected_item2.rules);
    ASSERT_EQ(converted_data.hierarchy_name, expected_item_data.hierarchy_name);
    ASSERT_EQ(converted_data.discount.name, expected_item_data.discount.name);
    ASSERT_EQ(converted_data.discount.values_with_schedules.size(), 1);

    auto converted_discounts_value =
        std::get<clients::eats_discounts::libraries::discounts::
                     FractionValueWithMaximum>(
            converted_data.discount.values_with_schedules.front()
                .money_value.menu_value.AsVariant());
    auto expected_discounts_value =
        std::get<clients::eats_discounts::libraries::discounts::
                     FractionValueWithMaximum>(
            expected_item_data.discount.values_with_schedules.front()
                .money_value.menu_value.AsVariant());

    ASSERT_EQ(utils::FromString<double>(converted_discounts_value.value),
              utils::FromString<double>(expected_discounts_value.value));

    auto converted_json_schedule = Serialize(
        converted_data.discount.values_with_schedules.front().schedule,
        formats::serialize::To<formats::json::Value>{});
    auto expected_json_schedule = Serialize(
        expected_item_data.discount.values_with_schedules.front().schedule,
        formats::serialize::To<formats::json::Value>{});
    ASSERT_EQ(converted_json_schedule, expected_json_schedule);
  }
}

TEST(GetCreateDiscountsData, FreeDeliveryTable) {
  clients::eats_discounts::PartnersDiscountCreateData expected_item1 =
      formats::json::FromString(R"(
{
  "rules": [
    {
      "condition_name": "place",
      "values": [
        1,
        2
      ]
    },
    {
      "condition_name": "active_period",
      "values": [
        {
          "start": "2021-10-29T21:00:00+00:00",
          "is_start_utc": true,
          "end": "2021-10-31T21:00:00+00:00",
          "is_end_utc": true
        }
      ]
    },
    {
      "condition_name": "brand_orders_count",
      "values": [
        {
          "start": 0,
          "end": 1
        }
      ]
    },
    {
      "condition_name": "delivery_method",
      "values": [
        "pedestrian"
      ]
    }
  ],
  "data": {
    "hierarchy_name": "place_delivery_discounts",
    "discount": {
      "name": "free_delivery",
      "values_with_schedules": [
        {
          "schedule": {
            "timezone": "LOCAL",
            "intervals": [
              {
                "exclude": false,
                "day": [
                  1,
                  2,
                  3,
                  4,
                  5,
                  6,
                  7
                ]
              }
            ]
          },
          "money_value": {
            "menu_value": {
              "value": [
                {
                  "from_cost": "300",
                  "discount": {
                    "value": "100.0",
                    "value_type": "fraction"
                  }
                }
              ],
              "value_type": "table"
            }
          }
        }
      ],
      "discount_meta": {
        "promo": {
          "name": "Бесплатная доставка от 300 руб.",
          "description": "На первый заказ от 300₽ в этом ресторане.",
          "picture_uri": "picture_uri"
        }
      }
    }
  }
}
)")
          .As<clients::eats_discounts::PartnersDiscountCreateData>();

  clients::eats_discounts::PartnersDiscountCreateData expected_item2 =
      formats::json::FromString(R"(
{
  "rules": [
    {
      "condition_name": "place",
      "values": [
        1,
        2
      ]
    },
    {
      "condition_name": "active_period",
      "values": [
        {
          "start": "2021-10-29T21:00:00+00:00",
          "is_start_utc": true,
          "end": "2021-10-31T21:00:00+00:00",
          "is_end_utc": true
        }
      ]
    },
    {
      "condition_name": "brand_orders_count",
      "values": [
        {
          "start": 0,
          "end": 1
        }
      ]
    },
    {
      "condition_name": "delivery_method",
      "values": [
        "pedestrian"
      ]
    }
  ],
  "data": {
    "hierarchy_name": "place_delivery_discounts",
    "discount": {
      "name": "free_delivery",
      "values_with_schedules": [
        {
          "schedule": {
            "timezone": "LOCAL",
            "intervals": [
              {
                "exclude": false,
                "day": [
                  1,
                  2,
                  3,
                  4,
                  5,
                  6,
                  7
                ]
              }
            ]
          },
          "money_value": {
            "menu_value": {
              "value": [
                {
                  "from_cost": "300",
                  "discount": {
                    "value": "100.0",
                    "value_type": "fraction"
                  }
                }
              ],
              "value_type": "table"
            }
          }
        }
      ],
      "discount_meta": {
        "promo": {
          "name": "Бесплатная доставка от 300 руб.",
          "description": "На первый заказ от 300₽ в этом ресторане.",
          "picture_uri": "picture_uri"
        }
      }
    }
  }
}
)")
          .As<clients::eats_discounts::PartnersDiscountCreateData>();

  auto promo_settings1 =
      formats::json::FromString(R"(
{
  "free_delivery": {
    "type": "free_delivery",
    "is_new": true,
    "enabled": false,
    "can_edit": false,
    "can_stop": true,
    "icon_url": "invalid.invalid",
    "can_pause": false,
    "can_create": true,
    "configuration": {
      "type": "free_delivery",
      "max_order_price": {
        "minimum": 0.0,
        "maximum": 10000.0
      }
    },
    "is_multiple_places_allowed": true,
    "hierarchy_name": "place_delivery_discounts"
  }
}
  )")
          .As<experiments3::eats_restapp_promo_settings::Value>();

  auto promo_settings2 =
      formats::json::FromString(R"(
{
  "free_delivery": {
    "type": "free_delivery",
    "is_new": true,
    "enabled": true,
    "can_edit": false,
    "can_stop": true,
    "icon_url": "invalid.invalid",
    "can_pause": false,
    "can_create": true,
    "configuration": {
      "type": "free_delivery",
      "max_order_price": {
        "minimum": 0.0,
        "maximum": 10000.0
      }
    },
    "is_multiple_places_allowed": true,
    "hierarchy_name": "place_delivery_discounts"
  }
}
  )")
          .As<experiments3::eats_restapp_promo_settings::Value>();

  eats_restapp_promo::models::PromoData promo_free_delivery{};
  promo_free_delivery.promo_type =
      eats_restapp_promo::models::PromoType::kFreeDelivery;
  promo_free_delivery.place_ids = {eats_restapp_promo::models::PlaceId{'1'},
                                   eats_restapp_promo::models::PlaceId{'2'}};

  promo_free_delivery.starts =
      utils::datetime::Stringtime("2021-10-29T21:00:00Z", "UTC");
  promo_free_delivery.ends =
      utils::datetime::Stringtime("2021-10-31T21:00:00Z", "UTC");

  eats_restapp_promo::models::PromoRequirement requirement;
  requirement.min_order_price = 300;
  promo_free_delivery.requirements = {requirement};

  taxi_config::eats_restapp_promo_free_delivery_create_settings::
      EatsRestappPromoFreeDeliveryCreateSettings settings;
  settings.disable_check = true;

  auto storage = dynamic_config::MakeDefaultStorage(
      {{taxi_config::EATS_RESTAPP_PROMO_FREE_DELIVERY_CREATE_SETTINGS,
        settings}});
  const auto config = storage.GetSnapshot();

  {
    const auto converted =
        eats_restapp_promo::utils::discounts::GetCreateDiscountsData(
            promo_free_delivery, config, promo_settings1);

    ASSERT_EQ(converted.size(), 1);

    auto converted_data =
        std::get<clients::eats_discounts::PlaceDeliveryDiscountData>(
            converted[0].data.AsVariant());
    auto expected_item_data =
        std::get<clients::eats_discounts::PlaceDeliveryDiscountData>(
            expected_item1.data.AsVariant());

    ASSERT_EQ(converted[0].rules, expected_item1.rules);
    ASSERT_EQ(converted_data.hierarchy_name, expected_item_data.hierarchy_name);
    ASSERT_EQ(converted_data.discount.name, expected_item_data.discount.name);
    ASSERT_EQ(converted_data.discount.values_with_schedules.size(), 1);

    auto converted_discounts_value =
        std::get<clients::eats_discounts::libraries::discounts::TableValue>(
            converted_data.discount.values_with_schedules.front()
                .money_value.menu_value.AsVariant())
            .value.front();
    auto expected_discounts_value =
        std::get<clients::eats_discounts::libraries::discounts::TableValue>(
            expected_item_data.discount.values_with_schedules.front()
                .money_value.menu_value.AsVariant())
            .value.front();

    ASSERT_EQ(utils::FromString<double>(converted_discounts_value.from_cost),
              utils::FromString<double>(expected_discounts_value.from_cost));

    auto converted_json_schedule = Serialize(
        converted_data.discount.values_with_schedules.front().schedule,
        formats::serialize::To<formats::json::Value>{});
    auto expected_json_schedule = Serialize(
        expected_item_data.discount.values_with_schedules.front().schedule,
        formats::serialize::To<formats::json::Value>{});
    ASSERT_EQ(converted_json_schedule, expected_json_schedule);
  }

  {
    const auto converted =
        eats_restapp_promo::utils::discounts::GetCreateDiscountsData(
            promo_free_delivery, config, promo_settings2);

    ASSERT_EQ(converted.size(), 1);

    auto converted_data =
        std::get<clients::eats_discounts::PlaceDeliveryDiscountData>(
            converted[0].data.AsVariant());
    auto expected_item_data =
        std::get<clients::eats_discounts::PlaceDeliveryDiscountData>(
            expected_item2.data.AsVariant());

    ASSERT_EQ(converted[0].rules, expected_item2.rules);
    ASSERT_EQ(converted_data.hierarchy_name, expected_item_data.hierarchy_name);
    ASSERT_EQ(converted_data.discount.name, expected_item_data.discount.name);
    ASSERT_EQ(converted_data.discount.values_with_schedules.size(), 1);

    auto converted_discounts_value =
        std::get<clients::eats_discounts::libraries::discounts::TableValue>(
            converted_data.discount.values_with_schedules.front()
                .money_value.menu_value.AsVariant())
            .value.front();
    auto expected_discounts_value =
        std::get<clients::eats_discounts::libraries::discounts::TableValue>(
            expected_item_data.discount.values_with_schedules.front()
                .money_value.menu_value.AsVariant())
            .value.front();

    ASSERT_EQ(utils::FromString<double>(converted_discounts_value.from_cost),
              utils::FromString<double>(expected_discounts_value.from_cost));

    auto converted_json_schedule = Serialize(
        converted_data.discount.values_with_schedules.front().schedule,
        formats::serialize::To<formats::json::Value>{});
    auto expected_json_schedule = Serialize(
        expected_item_data.discount.values_with_schedules.front().schedule,
        formats::serialize::To<formats::json::Value>{});
    ASSERT_EQ(converted_json_schedule, expected_json_schedule);
  }
}

inline eats_restapp_promo::types::PartnersDiscountMeta MakeMeta() {
  return {"some_name", "some_description", "some_uri"};
}

TEST(GetDiscountRequesDatatFromDicountData,
     PromoOnePlusOneRequestWithDefaulrSchhedule) {
  auto expected_result = formats::json::FromString(R"([
{
  "data": {
    "hierarchy_name": "restaurant_menu_discounts",
    "discount": {
      "name": "one_plus_one",
      "discount_meta": {
        "promo": {
          "description": "some_description",
          "name": "some_name",
          "picture_uri": "some_uri"
        }
      },
      "values_with_schedules": [
        {
          "product_value": {
            "discount_value": "100",
            "bundle": 2
          },
          "schedule": {
            "intervals": [
              {
                "day": [
                  1,
                  2,
                  3,
                  4,
                  5,
                  6,
                  7
                ],
                "exclude": false
              }
            ],
            "timezone": "LOCAL"
          }
        }
      ]
    }
  },
  "rules": [
    {
      "condition_name": "product",
      "values": [
        "1",
        "2",
        "3"
      ]
    },
    {
      "condition_name": "active_period",
      "values": [
        {
          "start": "2001-02-02T00:00:00+00:00",
          "end": "2001-04-02T00:00:00+00:00",
          "is_start_utc": true,
          "is_end_utc": true
        }
      ]
    },
    {
      "condition_name": "place",
      "values": [
        1, 2
      ]
    }
  ]
}
  ])");
  const auto starts = ::utils::datetime::Stringtime("2001-02-02T00:00:00Z");
  const auto ends = ::utils::datetime::Stringtime("2001-04-02T00:00:00Z");
  const auto discount_schedule =
      eats_restapp_promo::utils::ConvertScheduleToSchedule({});
  eats_restapp_promo::types::DiscountDataRaw discount_data = {
      {},
      std::vector<int64_t>{1, 2},
      {},
      {},
      {},
      {},
      ::defs::internal::discount_data::ActivePeriod{starts, ends, true, true},
      discount_schedule,
      {},
      std::vector<std::string>{"1", "2", "3"},
      {},
      {},
      {},
      {},
      {},
      {}};
  auto result = eats_restapp_promo::utils::discounts::
      GetDiscountRequesDatatFromDicountData(
          discount_data, handlers::TypeOfPromo::kOnePlusOne, MakeMeta(),
          "restaurant_menu_discounts", false);
  ASSERT_EQ(Serialize(result, formats::serialize::To<formats::json::Value>{}),
            expected_result);
}

TEST(GetDiscountRequesDatatFromDicountData,
     PromoOnePlusOneRequestWithSchedule) {
  auto expected_result = formats::json::FromString(R"([
{
  "data": {
    "hierarchy_name": "restaurant_menu_discounts",
    "discount": {
      "name": "one_plus_one",
      "discount_meta": {
        "promo": {
          "description": "some_description",
          "name": "some_name",
          "picture_uri": "some_uri"
        }
      },
      "values_with_schedules": [
        {
          "product_value": {
            "discount_value": "100",
            "bundle": 2
          },
          "schedule": {
            "intervals": [
              {
                "day": [
                  1,
                  3
                ],
                "exclude": false
              },
              {
                "daytime": [
                  {
                    "to": "16:40:00"
                  }
                ],
                "exclude": false
              }
            ],
            "timezone": "LOCAL"
          }
        },
        {
          "product_value": {
            "discount_value": "100",
            "bundle": 2
          },
          "schedule": {
            "intervals": [
              {
                "day": [
                  4
                ],
                "exclude": false
              },
              {
                "daytime": [
                  {
                    "from": "16:39:00",
                    "to": "16:40:00"
                  }
                ],
                "exclude": false
              }
            ],
            "timezone": "LOCAL"
          }
        }
      ]
    }
  },
  "rules": [
    {
      "condition_name": "product",
      "values": [
        "1",
        "2",
        "3"
      ]
    },
    {
      "condition_name": "active_period",
      "values": [
        {
          "start": "2001-02-02T00:00:00+00:00",
          "end": "2001-04-02T00:00:00+00:00",
          "is_start_utc": true,
          "is_end_utc": true
        }
      ]
    },
    {
      "condition_name": "place",
      "values": [
        1, 2
      ]
    }
  ]
}
  ])");
  const auto starts = ::utils::datetime::Stringtime("2001-02-02T00:00:00Z");
  const auto ends = ::utils::datetime::Stringtime("2001-04-02T00:00:00Z");
  std::vector<handlers::PromoSchedule> shedule = {
      handlers::PromoSchedule{1, 0, 1000}, handlers::PromoSchedule{3, 0, 1000},
      handlers::PromoSchedule{4, 999, 1000}};
  const auto discount_schedule =
      eats_restapp_promo::utils::ConvertScheduleToSchedule(shedule);
  eats_restapp_promo::types::DiscountDataRaw discount_data = {
      {},
      std::vector<int64_t>{1, 2},
      {},
      {},
      {},
      {},
      ::defs::internal::discount_data::ActivePeriod{starts, ends, true, true},
      discount_schedule,
      {},
      std::vector<std::string>{"1", "2", "3"},
      {},
      {},
      {},
      {},
      {},
      {}};
  auto result = eats_restapp_promo::utils::discounts::
      GetDiscountRequesDatatFromDicountData(
          discount_data, handlers::TypeOfPromo::kOnePlusOne, MakeMeta(),
          "restaurant_menu_discounts", false);
  ASSERT_EQ(Serialize(result, formats::serialize::To<formats::json::Value>{}),
            expected_result);
}

TEST(GetDiscountRequesDatatFromDicountData, PromoGiftRequest) {
  auto expected_result = formats::json::FromString(R"([
{
  "data": {
    "hierarchy_name": "restaurant_discounts",
    "discount": {
      "name": "gift",
      "discount_meta": {
        "promo": {
          "description": "some_description",
          "name": "some_name",
          "picture_uri": "some_uri"
        }
      },
      "values_with_schedules": [
        {
          "product_value": {
            "value": [
              {
                "step": {
                  "from_cost": "150",
                  "discount": "100"
                },
                "products": [
                  {
                    "id": "item_id"
                  }
                ],
                "bundle": 1
              }
            ]
          },
          "schedule": {
            "intervals": [
              {
                "day": [
                  1,
                  2,
                  3,
                  4,
                  5,
                  6,
                  7
                ],
                "exclude": false
              }
            ],
            "timezone": "LOCAL"
          }
        }
      ]
    }
  },
  "rules": [
    {
      "condition_name": "active_period",
      "values": [
        {
          "start": "2001-02-02T00:00:00+00:00",
          "end": "2001-04-02T00:00:00+00:00",
          "is_start_utc": true,
          "is_end_utc": true
        }
      ]
    },
    {
      "condition_name": "place",
      "values": [
        1, 2
      ]
    }
  ]
}
  ])");
  const auto starts = ::utils::datetime::Stringtime("2001-02-02T00:00:00Z");
  const auto ends = ::utils::datetime::Stringtime("2001-04-02T00:00:00Z");
  const auto discount_schedule =
      eats_restapp_promo::utils::ConvertScheduleToSchedule({});
  ::defs::internal::discount_data::OrderPrice order_price = {"150", "200"};
  eats_restapp_promo::types::DiscountDataRaw discount_data = {
      order_price,
      std::vector<int64_t>{1, 2},
      {},
      {},
      {},
      {},
      ::defs::internal::discount_data::ActivePeriod{starts, ends, true, true},
      discount_schedule,
      "item_id",
      {},
      {},
      {},
      {},
      {},
      {},
      {}};
  auto result = eats_restapp_promo::utils::discounts::
      GetDiscountRequesDatatFromDicountData(
          discount_data, handlers::TypeOfPromo::kGift, MakeMeta(),
          "restaurant_discounts", false);
  ASSERT_EQ(Serialize(result, formats::serialize::To<formats::json::Value>{}),
            expected_result);
}

TEST(GetDiscountRequesDatatFromDicountData, PromoGiftRequestWithoutOrderPrice) {
  auto expected_result = formats::json::FromString(R"([])");
  const auto starts = ::utils::datetime::Stringtime("2001-02-02T00:00:00Z");
  const auto ends = ::utils::datetime::Stringtime("2001-04-02T00:00:00Z");
  const auto discount_schedule =
      eats_restapp_promo::utils::ConvertScheduleToSchedule({});
  eats_restapp_promo::types::DiscountDataRaw discount_data = {
      {},
      std::vector<int64_t>{1, 2},
      {},
      {},
      {},
      {},
      ::defs::internal::discount_data::ActivePeriod{starts, ends, true, true},
      discount_schedule,
      "item_id",
      {},
      {},
      {},
      {},
      {},
      {},
      {}};
  auto result = eats_restapp_promo::utils::discounts::
      GetDiscountRequesDatatFromDicountData(
          discount_data, handlers::TypeOfPromo::kGift, MakeMeta(),
          "restaurant_discounts", false);
  ASSERT_EQ(Serialize(result, formats::serialize::To<formats::json::Value>{}),
            expected_result);
}

TEST(GetDiscountRequesDatatFromDicountData, PromoGiftRequestWithoutItemId) {
  auto expected_result = formats::json::FromString(R"([])");
  const auto starts = ::utils::datetime::Stringtime("2001-02-02T00:00:00Z");
  const auto ends = ::utils::datetime::Stringtime("2001-04-02T00:00:00Z");
  const auto discount_schedule =
      eats_restapp_promo::utils::ConvertScheduleToSchedule({});
  ::defs::internal::discount_data::OrderPrice order_price = {"150", "200"};
  eats_restapp_promo::types::DiscountDataRaw discount_data = {
      order_price,
      std::vector<int64_t>{1, 2},
      {},
      {},
      {},
      {},
      ::defs::internal::discount_data::ActivePeriod{starts, ends, true, true},
      discount_schedule,
      {},
      {},
      {},
      {},
      {},
      {},
      {},
      {}};
  auto result = eats_restapp_promo::utils::discounts::
      GetDiscountRequesDatatFromDicountData(
          discount_data, handlers::TypeOfPromo::kGift, MakeMeta(),
          "restaurant_discounts", false);
  ASSERT_EQ(Serialize(result, formats::serialize::To<formats::json::Value>{}),
            expected_result);
}

TEST(GetDiscountRequesDatatFromDicountData,
     PromoDiscountRequestDiscountForAllMenu) {
  auto expected_result = formats::json::FromString(R"([
{
  "data": {
    "hierarchy_name": "restaurant_menu_discounts",
    "discount": {
      "name": "discount",
      "discount_meta": {
        "promo": {
          "description": "some_description",
          "name": "some_name",
          "picture_uri": "some_uri"
        }
      },
      "values_with_schedules": [
        {
          "money_value": {
            "menu_value": {
              "value_type": "fraction",
              "value": "50"
            }
          },
          "schedule": {
            "intervals": [
              {
                "day": [
                  1,
                  2,
                  3,
                  4,
                  5,
                  6,
                  7
                ],
                "exclude": false
              }
            ],
            "timezone": "LOCAL"
          }
        }
      ]
    }
  },
  "rules": [
    {
      "condition_name": "active_period",
      "values": [
        {
          "start": "2001-02-02T00:00:00+00:00",
          "end": "2001-04-02T00:00:00+00:00",
          "is_start_utc": true,
          "is_end_utc": true
        }
      ]
    },
    {
      "condition_name": "place",
      "values": [
        1, 2
      ]
    }
  ]
}
  ])");
  const auto starts = ::utils::datetime::Stringtime("2001-02-02T00:00:00Z");
  const auto ends = ::utils::datetime::Stringtime("2001-04-02T00:00:00Z");
  const auto discount_schedule =
      eats_restapp_promo::utils::ConvertScheduleToSchedule({});
  eats_restapp_promo::types::DiscountDataRaw discount_data = {
      {},
      std::vector<int64_t>{1, 2},
      {},
      {},
      {},
      {},
      ::defs::internal::discount_data::ActivePeriod{starts, ends, true, true},
      discount_schedule,
      {},
      {},
      handlers::Discount{50, {}},
      {},
      {},
      {},
      {},
      {}};
  auto result = eats_restapp_promo::utils::discounts::
      GetDiscountRequesDatatFromDicountData(
          discount_data, handlers::TypeOfPromo::kDiscount, MakeMeta(),
          "restaurant_menu_discounts", false);
  ASSERT_EQ(Serialize(result, formats::serialize::To<formats::json::Value>{}),
            expected_result);
}

TEST(GetDiscountRequesDatatFromDicountData,
     PromoDiscountRequestDiscountForAllMenuWithMaximum) {
  auto expected_result = formats::json::FromString(R"([
{
  "data": {
    "hierarchy_name": "restaurant_menu_discounts",
    "discount": {
      "name": "discount",
      "discount_meta": {
        "promo": {
          "description": "some_description",
          "name": "some_name",
          "picture_uri": "some_uri"
        }
      },
      "values_with_schedules": [
        {
          "money_value": {
            "menu_value": {
              "value_type": "fraction",
              "maximum_discount": "1000",
              "value": "50"
            }
          },
          "schedule": {
            "intervals": [
              {
                "day": [
                  1,
                  2,
                  3,
                  4,
                  5,
                  6,
                  7
                ],
                "exclude": false
              }
            ],
            "timezone": "LOCAL"
          }
        }
      ]
    }
  },
  "rules": [
    {
      "condition_name": "active_period",
      "values": [
        {
          "start": "2001-02-02T00:00:00+00:00",
          "end": "2001-04-02T00:00:00+00:00",
          "is_start_utc": true,
          "is_end_utc": true
        }
      ]
    },
    {
      "condition_name": "place",
      "values": [
        1, 2
      ]
    }
  ]
}
  ])");
  const auto starts = ::utils::datetime::Stringtime("2001-02-02T00:00:00Z");
  const auto ends = ::utils::datetime::Stringtime("2001-04-02T00:00:00Z");
  const auto discount_schedule =
      eats_restapp_promo::utils::ConvertScheduleToSchedule({});
  eats_restapp_promo::types::DiscountDataRaw discount_data = {
      {},
      std::vector<int64_t>{1, 2},
      {},
      {},
      {},
      {},
      ::defs::internal::discount_data::ActivePeriod{starts, ends, true, true},
      discount_schedule,
      {},
      {},
      handlers::Discount{50, 1000.0},
      {},
      {},
      {},
      {},
      {}};
  auto result = eats_restapp_promo::utils::discounts::
      GetDiscountRequesDatatFromDicountData(
          discount_data, handlers::TypeOfPromo::kDiscount, MakeMeta(),
          "restaurant_menu_discounts", false);
  ASSERT_EQ(Serialize(result, formats::serialize::To<formats::json::Value>{}),
            expected_result);
}

TEST(GetDiscountRequesDatatFromDicountData, PromoDiscountRequestFixedDiscount) {
  auto expected_result = formats::json::FromString(R"([
{
  "data": {
    "hierarchy_name": "restaurant_menu_discounts",
    "discount": {
      "name": "discount",
      "discount_meta": {
        "promo": {
          "description": "some_description",
          "name": "some_name",
          "picture_uri": "some_uri"
        }
      },
      "values_with_schedules": [
        {
          "money_value": {
            "menu_value": {
              "value_type": "absolute",
              "value": "50"
            }
          },
          "schedule": {
            "intervals": [
              {
                "day": [
                  1,
                  2,
                  3,
                  4,
                  5,
                  6,
                  7
                ],
                "exclude": false
              }
            ],
            "timezone": "LOCAL"
          }
        }
      ]
    }
  },
  "rules": [
    {
      "condition_name": "active_period",
      "values": [
        {
          "start": "2001-02-02T00:00:00+00:00",
          "end": "2001-04-02T00:00:00+00:00",
          "is_start_utc": true,
          "is_end_utc": true
        }
      ]
    },
    {
      "condition_name": "place",
      "values": [
        1, 2
      ]
    }
  ]
}
  ])");
  const auto starts = ::utils::datetime::Stringtime("2001-02-02T00:00:00Z");
  const auto ends = ::utils::datetime::Stringtime("2001-04-02T00:00:00Z");
  const auto discount_schedule =
      eats_restapp_promo::utils::ConvertScheduleToSchedule({});
  eats_restapp_promo::types::DiscountDataRaw discount_data = {
      {},
      std::vector<int64_t>{1, 2},
      {},
      {},
      {},
      {},
      ::defs::internal::discount_data::ActivePeriod{starts, ends, true, true},
      discount_schedule,
      {},
      {},
      {},
      {},
      {},
      {},
      50.0,
      {}};
  auto result = eats_restapp_promo::utils::discounts::
      GetDiscountRequesDatatFromDicountData(
          discount_data, handlers::TypeOfPromo::kDiscount, MakeMeta(),
          "restaurant_menu_discounts", false);
  ASSERT_EQ(Serialize(result, formats::serialize::To<formats::json::Value>{}),
            expected_result);
}

TEST(GetDiscountRequesDatatFromDicountData,
     PromoDiscountRequestDiscountForSomeMenu) {
  auto expected_result = formats::json::FromString(R"([
{
  "data": {
    "hierarchy_name": "restaurant_menu_discounts",
    "discount": {
      "name": "discount",
      "discount_meta": {
        "promo": {
          "description": "some_description",
          "name": "some_name",
          "picture_uri": "some_uri"
        }
      },
      "values_with_schedules": [
        {
          "money_value": {
            "menu_value": {
              "value_type": "fraction",
              "value": "50"
            }
          },
          "schedule": {
            "intervals": [
              {
                "day": [
                  1,
                  2,
                  3,
                  4,
                  5,
                  6,
                  7
                ],
                "exclude": false
              }
            ],
            "timezone": "LOCAL"
          }
        }
      ]
    }
  },
  "rules": [
    {
      "condition_name": "product",
      "values": [
        "1",
        "2",
        "3"
      ]
    },
    {
      "condition_name": "active_period",
      "values": [
        {
          "start": "2001-02-02T00:00:00+00:00",
          "end": "2001-04-02T00:00:00+00:00",
          "is_start_utc": true,
          "is_end_utc": true
        }
      ]
    },
    {
      "condition_name": "place",
      "values": [
        1, 2
      ]
    }
  ]
}
  ])");
  const auto starts = ::utils::datetime::Stringtime("2001-02-02T00:00:00Z");
  const auto ends = ::utils::datetime::Stringtime("2001-04-02T00:00:00Z");
  const auto discount_schedule =
      eats_restapp_promo::utils::ConvertScheduleToSchedule({});
  eats_restapp_promo::types::DiscountDataRaw discount_data = {
      {},
      std::vector<int64_t>{1, 2},
      {},
      {},
      {},
      {},
      ::defs::internal::discount_data::ActivePeriod{starts, ends, true, true},
      discount_schedule,
      {},
      std::vector<std::string>{"1", "2", "3"},
      handlers::Discount{50, {}},
      {},
      {},
      {},
      {},
      {}};
  auto result = eats_restapp_promo::utils::discounts::
      GetDiscountRequesDatatFromDicountData(
          discount_data, handlers::TypeOfPromo::kDiscount, MakeMeta(),
          "restaurant_menu_discounts", false);
  ASSERT_EQ(Serialize(result, formats::serialize::To<formats::json::Value>{}),
            expected_result);
}

TEST(GetDiscountRequesDatatFromDicountData,
     PromoDiscountRequestDiscountForEmptySchedule) {
  const auto starts = ::utils::datetime::Stringtime("2001-02-02T00:00:00Z");
  const auto ends = ::utils::datetime::Stringtime("2001-04-02T00:00:00Z");
  std::vector<handlers::PromoSchedule> shedule;
  const auto discount_schedule =
      eats_restapp_promo::utils::ConvertScheduleToSchedule(shedule);
  eats_restapp_promo::types::DiscountDataRaw discount_data = {
      {},
      std::vector<int64_t>{1, 2},
      {},
      {},
      {},
      {},
      ::defs::internal::discount_data::ActivePeriod{starts, ends, true, true},
      discount_schedule,
      {},
      std::vector<std::string>{"1", "2", "3"},
      handlers::Discount{50, {}},
      {},
      {},
      {},
      {},
      {}};
  ASSERT_THROW(eats_restapp_promo::utils::discounts::
                   GetDiscountRequesDatatFromDicountData(
                       discount_data, handlers::TypeOfPromo::kDiscount,
                       MakeMeta(), "restaurant_menu_discounts", false),
               formats::json::Exception);
}

TEST(GetDiscountRequesDatatFromDicountData,
     PromoDiscountRequestDiscountForEmptyDiscountData) {
  auto expected_result = formats::json::FromString(R"([])");
  eats_restapp_promo::types::DiscountDataRaw discount_data = {
      {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}};
  auto result = eats_restapp_promo::utils::discounts::
      GetDiscountRequesDatatFromDicountData(
          discount_data, handlers::TypeOfPromo::kDiscount, MakeMeta(),
          "restaurant_menu_discounts", false);
  ASSERT_EQ(Serialize(result, formats::serialize::To<formats::json::Value>{}),
            expected_result);
}

TEST(GetDiscountRequesDatatFromDicountData,
     PromoOnePlusOneRequestDiscountForEmptyDiscountData) {
  auto expected_result = formats::json::FromString(R"([
{
  "data": {
    "hierarchy_name": "restaurant_menu_discounts",
    "discount": {
      "name": "one_plus_one",
      "discount_meta": {
        "promo": {
          "description": "some_description",
          "name": "some_name",
          "picture_uri": "some_uri"
        }
      },
      "values_with_schedules": [
        {
          "product_value": {
            "discount_value": "100",
            "bundle": 2
          },
          "schedule": {
            "intervals": [
              {
                "day": [
                  1,
                  2,
                  3,
                  4,
                  5,
                  6,
                  7
                ],
                "exclude": false
              }
            ],
            "timezone": "LOCAL"
          }
        }
      ]
    }
  },
  "rules": [
    {
      "condition_name": "active_period",
      "values": [
        {
          "start": "1970-01-01T00:00:00+00:00",
          "is_start_utc" :false,
          "end": "1970-01-01T00:00:00+00:00",
          "is_end_utc": false
        }
      ]
    },
    {
      "condition_name": "place",
      "values": []
    }
  ]
}
  ])");
  const auto discount_schedule =
      eats_restapp_promo::utils::ConvertScheduleToSchedule({});
  eats_restapp_promo::types::DiscountDataRaw discount_data = {
      {}, {}, {}, {}, {}, {}, {}, discount_schedule,
      {}, {}, {}, {}, {}, {}, {}, {}};
  auto result = eats_restapp_promo::utils::discounts::
      GetDiscountRequesDatatFromDicountData(
          discount_data, handlers::TypeOfPromo::kOnePlusOne, MakeMeta(),
          "restaurant_menu_discounts", false);
  ASSERT_EQ(Serialize(result, formats::serialize::To<formats::json::Value>{}),
            expected_result);
}

TEST(GetDiscountRequesDatatFromDicountData, PromoGiftRequestForProgressive) {
  auto expected_result = formats::json::FromString(R"([
{
  "data": {
    "hierarchy_name": "restaurant_discounts",
    "discount": {
      "name": "gift",
      "discount_meta": {
        "promo": {
          "description": "some_description",
          "name": "some_name",
          "picture_uri": "some_uri"
        }
      },
      "values_with_schedules": [
        {
          "product_value": {
            "value": [
              {
                "step": {
                  "from_cost": "150",
                  "discount": "100"
                },
                "products": [
                  {
                    "id": "item_id1"
                  },
                  {
                    "id": "item_id2"
                  }
                ],
                "bundle": 1
              },
              {
                "step": {
                  "from_cost": "250",
                  "discount": "100"
                },
                "products": [
                  {
                    "id": "item_id3"
                  }
                ],
                "bundle": 1
              }
            ]
          },
          "schedule": {
            "intervals": [
              {
                "day": [
                  1,
                  2,
                  3,
                  4,
                  5,
                  6,
                  7
                ],
                "exclude": false
              }
            ],
            "timezone": "LOCAL"
          }
        }
      ]
    }
  },
  "rules": [
    {
      "condition_name": "active_period",
      "values": [
        {
          "start": "2001-02-02T00:00:00+00:00",
          "end": "2001-04-02T00:00:00+00:00",
          "is_start_utc": true,
          "is_end_utc": true
        }
      ]
    },
    {
      "condition_name": "place",
      "values": [
        1, 2
      ]
    }
  ]
}
  ])");
  const auto starts = ::utils::datetime::Stringtime("2001-02-02T00:00:00Z");
  const auto ends = ::utils::datetime::Stringtime("2001-04-02T00:00:00Z");
  const auto discount_schedule =
      eats_restapp_promo::utils::ConvertScheduleToSchedule({});
  std::vector<::defs::internal::discount_data::Progressive> progressive = {
      {{"150", "100"}, {{"item_id1"}, {"item_id2"}}},
      {{"250", "100"}, {{"item_id3"}}}};
  eats_restapp_promo::types::DiscountDataRaw discount_data = {
      {},
      std::vector<int64_t>{1, 2},
      {},
      {},
      {},
      {},
      ::defs::internal::discount_data::ActivePeriod{starts, ends, true, true},
      discount_schedule,
      {},
      {},
      {},
      {},
      {},
      progressive,
      {},
      {}};
  auto result = eats_restapp_promo::utils::discounts::
      GetDiscountRequesDatatFromDicountData(
          discount_data, handlers::TypeOfPromo::kGift, MakeMeta(),
          "restaurant_discounts", false);
  ASSERT_EQ(Serialize(result, formats::serialize::To<formats::json::Value>{}),
            expected_result);
}

TEST(GetDiscountRequesDatatFromDicountData, RequestWithDifferentParams) {
  auto expected_result = formats::json::FromString(R"([
{
  "data": {
    "hierarchy_name": "restaurant_discounts",
    "discount": {
      "name": "gift",
      "discount_meta": {
        "promo": {
          "description": "some_description",
          "name": "some_name",
          "picture_uri": "some_uri"
        }
      },
      "values_with_schedules": [
        {
          "product_value": {
            "value": [
              {
                "step": {
                  "from_cost": "150",
                  "discount": "100"
                },
                "products": [
                  {
                    "id": "item_id"
                  }
                ],
                "bundle": 1
              }
            ]
          },
          "schedule": {
            "intervals": [
              {
                "day": [
                  1,
                  2,
                  3,
                  4,
                  5,
                  6,
                  7
                ],
                "exclude": false
              }
            ],
            "timezone": "LOCAL"
          }
        }
      ]
    }
  },
  "rules": [
    {
      "condition_name": "product",
      "values": [
        "1",
        "2",
        "3"
      ]
    },
    {
      "condition_name": "active_period",
      "values": [
        {
          "start": "2001-02-02T00:00:00+00:00",
          "end": "2001-04-02T00:00:00+00:00",
          "is_start_utc": true,
          "is_end_utc": true
        }
      ]
    },
    {
      "condition_name": "place",
      "values": [
        1, 2
      ]
    },
    {
      "condition_name" : "brand_time_from_last_order_range",
      "values": [
        {
          "start": 5,
          "end": 52000000
        }
      ]
    },
    {
      "condition_name": "shipping_type",
      "values": [
        "method1", "method2"
      ]
    }
  ]
},
{
  "data": {
    "hierarchy_name": "restaurant_discounts",
    "discount": {
      "name": "gift",
      "discount_meta": {
        "promo": {
          "description": "some_description",
          "name": "some_name",
          "picture_uri": "some_uri"
        }
      },
      "values_with_schedules": [
        {
          "money_value": {
            "menu_value": {
              "value_type": "fraction",
              "value": "50"
            }
          },
          "schedule": {
            "intervals": [
              {
                "day": [
                  1,
                  2,
                  3,
                  4,
                  5,
                  6,
                  7
                ],
                "exclude": false
              }
            ],
            "timezone": "LOCAL"
          }
        }
      ]
    }
  },
  "rules": [
    {
      "condition_name": "product",
      "values": [
        "1",
        "2",
        "3"
      ]
    },
    {
      "condition_name": "active_period",
      "values": [
        {
          "start": "2001-02-02T00:00:00+00:00",
          "end": "2001-04-02T00:00:00+00:00",
          "is_start_utc": true,
          "is_end_utc": true
        }
      ]
    },
    {
      "condition_name": "place",
      "values": [
        1, 2
      ]
    },
    {
      "condition_name" : "brand_time_from_last_order_range",
      "values": [
        {
          "start": 5,
          "end": 52000000
        }
      ]
    },
    {
      "condition_name": "shipping_type",
      "values": [
        "method1", "method2"
      ]
    }
  ]
}
  ])");
  const auto starts = ::utils::datetime::Stringtime("2001-02-02T00:00:00Z");
  const auto ends = ::utils::datetime::Stringtime("2001-04-02T00:00:00Z");
  const auto discount_schedule =
      eats_restapp_promo::utils::ConvertScheduleToSchedule({});
  ::defs::internal::discount_data::OrderPrice order_price = {"150", "200"};
  eats_restapp_promo::types::DiscountDataRaw discount_data = {
      order_price,
      std::vector<int64_t>{1, 2},
      {},
      {},
      {},
      {},
      ::defs::internal::discount_data::ActivePeriod{starts, ends, true, true},
      discount_schedule,
      "item_id",
      std::vector<std::string>{"1", "2", "3"},
      handlers::Discount{50, {}},
      {},
      ::defs::internal::discount_data::DaysFromLastOrder{5, 52000000},
      {},
      {},
      std::vector<std::string>{"method1", "method2"}};
  auto result = eats_restapp_promo::utils::discounts::
      GetDiscountRequesDatatFromDicountData(
          discount_data, handlers::TypeOfPromo::kGift, MakeMeta(),
          "restaurant_discounts", false);
  ASSERT_EQ(Serialize(result, formats::serialize::To<formats::json::Value>{}),
            expected_result);
  ASSERT_THROW(eats_restapp_promo::utils::discounts::
                   GetDiscountRequesDatatFromDicountData(
                       discount_data, handlers::TypeOfPromo::kDiscount,
                       MakeMeta(), "restaurant_menu_discounts", false),
               formats::json::Exception);
  ASSERT_THROW(eats_restapp_promo::utils::discounts::
                   GetDiscountRequesDatatFromDicountData(
                       discount_data, handlers::TypeOfPromo::kOnePlusOne,
                       MakeMeta(), "restaurant_menu_discounts", false),
               formats::json::Exception);
}

TEST(GetDiscountRequesDatatFromDicountData, CheckRules) {
  auto expected_result = formats::json::FromString(R"([
{
  "data": {
    "hierarchy_name": "restaurant_menu_discounts",
    "discount": {
      "name": "one_plus_one",
      "discount_meta": {
        "promo": {
          "description": "some_description",
          "name": "some_name",
          "picture_uri": "some_uri"
        }
      },
      "values_with_schedules": [
        {
          "product_value": {
            "discount_value": "100",
            "bundle": 2
          },
          "schedule": {
            "intervals": [
              {
                "day": [
                  1,
                  2,
                  3,
                  4,
                  5,
                  6,
                  7
                ],
                "exclude": false
              }
            ],
            "timezone": "LOCAL"
          }
        }
      ]
    }
  },
  "rules": [
    {
      "condition_name": "product",
      "values": [
        "1",
        "2",
        "3"
      ]
    },
    {
      "condition_name": "active_period",
      "values": [
        {
          "start": "2001-02-02T00:00:00+00:00",
          "end": "2001-04-02T00:00:00+00:00",
          "is_start_utc": true,
          "is_end_utc": true
        }
      ]
    },
    {
      "condition_name": "place",
      "values": [1, 2]
    },
    {
      "condition_name": "has_yaplus",
      "values": [1]
    },
    {
      "condition_name": "brand_orders_count",
      "values": [
        {
          "start": 0,
          "end": 1
        },
        {
          "start": 1,
          "end": 2
        }
      ]
    },
    {
      "condition_name": "delivery_method",
      "values": ["walking"]
    },
    {
      "condition_name": "brand_time_from_last_order_range",
      "values": [
        {
          "start": 0,
          "end": 1
        }
      ]
    },
    {
      "condition_name": "shipping_type",
      "values": ["type1", "type2"]
    }
  ]
}
  ])");
  const auto discount_schedule =
      eats_restapp_promo::utils::ConvertScheduleToSchedule({});
  const auto starts = ::utils::datetime::Stringtime("2001-02-02T00:00:00Z");
  const auto ends = ::utils::datetime::Stringtime("2001-04-02T00:00:00Z");
  eats_restapp_promo::types::DiscountDataRaw discount_data = {
      {},
      {1, 2},
      {},
      std::vector<::defs::internal::discount_data::BrandOrdersCount>{{0, 1},
                                                                     {1, 2}},
      std::vector<std::string>{"walking"},
      1,
      ::defs::internal::discount_data::ActivePeriod{starts, ends, true, true},
      discount_schedule,
      {},
      std::vector<std::string>{"1", "2", "3"},
      {},
      std::vector<::defs::internal::discount_data::PlaceOrdersCount>{{0, 1}},
      {{0, 1}},
      {},
      {},
      std::vector<std::string>{"type1", "type2"}};
  auto result = eats_restapp_promo::utils::discounts::
      GetDiscountRequesDatatFromDicountData(
          discount_data, handlers::TypeOfPromo::kOnePlusOne, MakeMeta(),
          "restaurant_menu_discounts", false);
  ASSERT_EQ(Serialize(result, formats::serialize::To<formats::json::Value>{}),
            expected_result);
}
