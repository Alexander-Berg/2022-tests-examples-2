import json


REGULAR_REQUEST_PAYLOAD = {
   "emergency_contact": {
      "phone": "+79161234567",
      "name": "string"
   },
   "client_requirements": {
      "taxi_class": "courier"
   },
   "requirements": {
      "soft_requirements": [
      ]
   },
   "custom_context": {
       "zone_type": "pedestrian",
       "weight_restrictions": [
      {
        "weight_gr": 15000,
        "moving_behavior": "pedestrian"
      },
      {
        "weight_gr": 22000,
        "moving_behavior": "bicycle"
      },
      {
        "weight_gr": 22000,
        "moving_behavior": "electrobike"
      },
      {
        "weight_gr": 52000,
        "moving_behavior": "auto"
      },
      {
        "weight_gr": 22000,
        "moving_behavior": "motorcycle"
      }
    ],
       "batch_weight_restrictions": [
      {
        "weight_gr": 26000,
        "moving_behavior": "pedestrian"
      },
      {
        "weight_gr": 26000,
        "moving_behavior": "bicycle"
      },
      {
        "weight_gr": 26000,
        "moving_behavior": "electrobike"
      },
      {
        "weight_gr": 56000,
        "moving_behavior": "auto"
      },
      {
        "weight_gr": 26000,
        "moving_behavior": "motorcycle"
      }
    ]
  },
   "special_requirements": {
      "virtual_tariffs": [
         {
            "class": "cargo",
            "special_requirements": [
               {
                  "id": "cargo_eds"
               },
               {
                  "id": "too_heavy_no_walking_courier"
               }
            ]
         },
         {
            "class": "cargocorp",
            "special_requirements": [
               {
                  "id": "cargo_eds"
               },
               {
                  "id": "too_heavy_no_walking_courier"
               }
            ]
         },
         {
            "class": "courier",
            "special_requirements": [
               {
                  "id": "cargo_eds"
               },
               {
                  "id": "too_heavy_no_walking_courier"
               }
            ]
         },
         {
            "class": "eda",
            "special_requirements": [
               {
                  "id": "cargo_eds"
               },
               {
                  "id": "too_heavy_no_walking_courier"
               }
            ]
         },
         {
            "class": "express",
            "special_requirements": [
               {
                  "id": "cargo_eds"
               },
               {
                  "id": "too_heavy_no_walking_courier"
               }
            ]
         },
         {
            "class": "lavka",
            "special_requirements": [
               {
                  "id": "cargo_eds"
               },
               {
                  "id": "too_heavy_no_walking_courier"
               }
            ]
         }
      ]
   },
   "items": [
        {
            "pickup_point": 1,
            "extra_id": "K34232",
            "droppof_point": 2,
            "title": "meow 2",
            "size": {
                "length": 0.1,
                "width": 0.1,
                "height": 0.1
            },
            "weight": 1,
            "quantity": 1,
            "cost_value": "100",
            "cost_currency": "RUB"
        }
   ],
    "route_points": [
        {
            "type": "source",
            "point_id": 1,
            "visit_order": 1,
            "address": {
                "time_interval": {
                    "from": "2020-01-01T00:00:00+0000",
                    "to": "2021-01-01T01:00:00+0000"
                },
                "fullname": "БЦ Аврора",
                "coordinates": [
                    37.642931,
                    55.734797
                ],
                "country": "Россия",
                "city": "Москва",
                "street": "Садовническая улица",
                "building": "82",
                "porch": "4",
                "door_code": "123#",
                "comment": "первая"
            },
            "contact": {
                "phone": "+79168498456",
                "name": "string"
            },
            "external_order_cost": {
                "currency": "RUB",
                "currency_sign": "R",
                "value": "100"
            },
            "external_order_id": "210323-472280",
            "skip_confirmation": True
        },
        {
            "type": "destination",
            "point_id": 2,
            "visit_order": 2,
            "address": {
                "time_interval": {
                    "from": "2020-01-01T00:00:00+0000",
                    "to": "2021-01-01T01:00:00+0000"
                },
                "fullname": "Ураина",
                "coordinates": [
                    37.661330,
                    55.733495
                ],
                "country": "Россия",
                "city": "Москва",
                "street": "Киевская",
                "building": "82",
                "porch": "4",
                "comment": "вторая точка коммент"
            },
            "contact": {
                "phone": "+79168498456",
                "name": "string",
                "email": "skulik@yandex-team.ru"
            },
            "external_order_cost": {
                "currency": "RUB",
                "currency_sign": "R",
                "value": "100"
            },
            "external_order_id": "210323-472280",
            "skip_confirmation": True
        },
        {
            "type": "return",
            "point_id": 3,
            "visit_order": 3,
            "address": {
                "time_interval": {
                    "from": "2020-01-01T00:00:00+0000",
                    "to": "2021-01-01T01:00:00+0000"
                },
                "fullname": "Ураина",
                "coordinates": [
                    37.642931,
                    55.734797
                ],
                "country": "Россия",
                "city": "Москва",
                "street": "Киевская",
                "building": "82",
                "porch": "4"
            },
            "contact": {
                "phone": "+79168498456",
                "name": "string",
                "email": "skulik@yandex-team.ru"
            },
            "skip_confirmation": True
        }
    ]
}

PULL_DISPATCH_REQUEST_PAYLOAD = {
    "requirements": {
        "soft_requirements": [
        ]
    },
    "claim_kind": "platform_usage",
    "emergency_contact": {
        "phone": "+79168498456",
        "name": "string"
    },
    "client_requirements": {
        "taxi_class": "courier"
    },
    "items": [
        {
            "pickup_point": 1,
            "extra_id": "K34232",
            "droppof_point": 2,
            "title": "meow 2",
            "size": {
                "length": 0.1,
                "width": 0.1,
                "height": 0.1
            },
            "weight": 1,
            "quantity": 1,
            "cost_value": "250",
            "cost_currency": "RUB"
        },
        {
            "pickup_point": 1,
            "extra_id": "K34232",
            "droppof_point": 3,
            "title": "meow 1",
            "size": {
                "length": 0.1,
                "width": 0.1,
                "height": 0.1
            },
            "weight": 1,
            "quantity": 1,
            "cost_value": "250",
            "cost_currency": "RUB"
        }
    ],
    "route_points": [
        {
            "type": "source",
            "point_id": 1,
            "visit_order": 1,
            "address": {
                "time_interval": {
                    "from": "2020-01-01T00:00:00+0000",
                    "to": "2021-01-01T01:00:00+0000"
                },
                "fullname": "Яндекс.Лавка",
                "coordinates": [
                    37.567051,
                    55.725326
                ],
                "country": "Россия",
                "city": "Москва",
                "street": "Кооперативная улица",
                "building": "2к4",
                "porch": "4",
                "door_code": "123#",
                "comment": "Lavka"
            },
            "contact": {
                "phone": "+79999999999",
                "name": "string"
            },
            "external_order_cost": {
                "currency": "RUB",
                "currency_sign": "R",
                "value": "100"
            },
            "external_order_id": "210323-472280",
            "skip_confirmation": True
        },
        {
            "type": "destination",
            "point_id": 2,
            "visit_order": 2,
            "address": {
                "time_interval": {
                    "from": "2020-01-01T00:00:00+0000",
                    "to": "2021-01-01T01:00:00+0000"
                },
                "fullname": "Доставка 1",
                "coordinates": [
                    37.570069,
                    55.722984
                ],
                "country": "Россия",
                "city": "Москва",
                "street": "улица Ефремова",
                "building": "16/12",
                "porch": "2",
                "flat":72,
                "comment": "тыц"
            },
            "contact": {
                "phone": "+79168498456",
                "name": "Аркадий",
                "email": "skulik@yandex-team.ru"
            },
            "external_order_cost": {
                "currency": "RUB",
                "currency_sign":"R",
                "value": "100"
            },
            "skip_confirmation": True
        },
        {
            "type": "destination",
            "point_id": 3,
            "visit_order": 3,
            "address": {
                "time_interval": {
                    "from": "2020-01-01T00:00:00+0000",
                    "to": "2021-01-01T01:00:00+0000"
                },
                "fullname": "Возврат на лавку",
                 "coordinates": [
                    37.567051,
                    55.725326
                ],
                "country": "Россия",
                "city": "Москва",
                "street": "Кооперативная улица",
                "building": "2к4",
                "porch": "4",
                "door_code": "123#",
                "comment": "Lavka"
            },
            "contact": {
                "phone": "+79168498456",
                "name": "Лавка",
                "email": "skulik@yandex-team.ru"
            },
            "external_order_cost": {
                "currency": "RUB",
                "currency_sign": "R",
                "value": "100"
            },
            "skip_confirmation": True
        },
        {
            "type": "return",
            "point_id": 4,
            "visit_order": 4,
            "address": {
                "time_interval": {
                    "from": "2020-01-01T00:00:00+0000",
                    "to": "2021-01-01T01:00:00+0000"
                },
                "fullname": "Яндекс.Лавка",
                "coordinates": [
                    37.567051,
                    55.725326
                ],
                "country": "Россия",
                "city": "Москва",
                "street": "Кооперативная улица",
                "building": "2к4",
                "porch": "4"
            },
            "contact": {
                "phone": "+79168498456",
                "name": "string",
                "email": "skulik@yandex-team.ru"
            },
            "skip_confirmation": True
        }
    ],
    "custom_context": {
        "dispatch_type": "pull-dispatch"
    }
}
