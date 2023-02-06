INSERT INTO eats_restapp_menu.menu_item_nutrients(place_id, origin_id, calories, proteins, fats, carbohydrates, deactivated_at)
VALUES
(109151, '1234595', 66.66, 77.77, 88.88, 99.99, NULL),
(109151, '123', 6.66, 7.77, 8.88, 9.99, NULL),
(109151, '10919869', 666.66, 777.77, 888.88, 999.99, '2020-01-01T04:04:04.000+00:00'::TIMESTAMPTZ);


INSERT INTO eats_restapp_menu.menu_content(place_id, menu_hash, menu_json)
VALUES (109151, 'same_hash', '
{
  "categories": [
    {
      "available": true,
      "id": "103263",
      "name": "Завтрак",
      "sortOrder": 130
    },
    {
      "available": true,
      "id": "103265",
      "name": "Закуски",
      "sortOrder": 160
    }
  ],
  "items": [
    {
      "available": true,
      "categoryId": "103263",
      "description": "",
      "id": "1234583",
      "images": [
        {
          "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d9.jpg"
        }
      ],
      "measure": 35,
      "measureUnit": "г",
      "menuItemId": 37660163,
      "modifierGroups": [],
      "name": "Сухофрукты",
      "price": 100,
      "sortOrder": 100,
      "thumbnails": [
        {
          "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d9-80x80.jpg"
        }
      ],
      "vat": 0
    },
    {
      "available": true,
      "categoryId": "103263",
      "description": "",
      "id": "1234595",
      "images": [
        {
          "url": "https://testing.eda.tst.yandex.net/images/1368744/9d2253f1d40f86ff4e525e998f49dfca.jpg"
        }
      ],
      "measure": 50,
      "measureUnit": "г",
      "menuItemId": 37660168,
      "modifierGroups": [],
      "name": "Сметана 20%",
      "nutrients": {
        "calories": "66.66",
        "carbohydrates": "99.99",
        "fats": "88.88",
        "is_deactivated": false,
        "proteins": "77.77"
      },
      "price": 100,
      "sortOrder": 100,
      "thumbnails": [
        {
          "url": "https://testing.eda.tst.yandex.net/images/1368744/9d2253f1d40f86ff4e525e998f49dfca-80x80.jpg"
        }
      ],
      "vat": 0
    },
    {
      "available": false,
      "categoryId": "103263",
      "description": "На воде или на молоке на выбор",
      "id": "10919869",
      "images": [
        {
          "url": "https://testing.eda.tst.yandex.net/images/1380157/40f79298b95c727bed8bc312bea05675.jpg"
        }
      ],
      "measure": 250.0,
      "measureUnit": "г",
      "menuItemId": 37660318,
      "modifierGroups": [
        {
          "id": "2716195",
          "maxSelectedModifiers": 1,
          "menuItemOptionGroupId": 12465033,
          "minSelectedModifiers": 1,
          "modifiers": [
            {
              "available": true,
              "id": "26783155",
              "maxAmount": 1,
              "menuItemOptionId": 93947398,
              "minAmount": 0,
              "name": "Молоко",
              "price": 0.0
            },
            {
              "available": true,
              "id": "26783158",
              "maxAmount": 1,
              "menuItemOptionId": 93947403,
              "minAmount": 0,
              "name": "Вода",
              "price": 0.0
            },
            {
              "available": true,
              "id": "26783164",
              "maxAmount": 1,
              "menuItemOptionId": 93947408,
              "minAmount": 0,
              "name": "На кокосовом молоке",
              "price": 0.0
            }
          ],
          "name": "Основа каши",
          "sortOrder": 100
        },
        {
          "id": "2716198",
          "maxSelectedModifiers": 4,
          "menuItemOptionGroupId": 12465038,
          "minSelectedModifiers": 0,
          "modifiers": [
            {
              "available": true,
              "id": "26783167",
              "maxAmount": 1,
              "menuItemOptionId": 93947413,
              "minAmount": 0,
              "name": "Малина протертая с сахаром",
              "price": 100.0
            },
            {
              "available": true,
              "id": "26783170",
              "maxAmount": 1,
              "menuItemOptionId": 93947418,
              "minAmount": 0,
              "name": "Клубника протертая с сахаром",
              "price": 100.0
            },
            {
              "available": true,
              "id": "26783173",
              "maxAmount": 1,
              "menuItemOptionId": 93947423,
              "minAmount": 0,
              "name": "Земляника протертая с сахаром",
              "price": 200.0
            },
            {
              "available": true,
              "id": "26783176",
              "maxAmount": 1,
              "menuItemOptionId": 93947428,
              "minAmount": 0,
              "name": "Клубника свежая",
              "price": 200.0
            }
          ],
          "name": "Дополнительные ингредиенты",
          "sortOrder": 100
        },
        {
          "id": "2716201",
          "maxSelectedModifiers": 8,
          "menuItemOptionGroupId": 12465043,
          "minSelectedModifiers": 0,
          "modifiers": [
            {
              "available": true,
              "id": "26783179",
              "maxAmount": 1,
              "menuItemOptionId": 93947433,
              "minAmount": 0,
              "name": "Банан (50 г)",
              "price": 100.0
            },
            {
              "available": true,
              "id": "26783182",
              "maxAmount": 1,
              "menuItemOptionId": 93947438,
              "minAmount": 0,
              "name": "Изюм (35 г)",
              "price": 100.0
            },
            {
              "available": true,
              "id": "26783185",
              "maxAmount": 1,
              "menuItemOptionId": 93947443,
              "minAmount": 0,
              "name": "Курага (35 г)",
              "price": 100.0
            },
            {
              "available": true,
              "id": "26783188",
              "maxAmount": 1,
              "menuItemOptionId": 93947448,
              "minAmount": 0,
              "name": "Грецкий орех (35 г)",
              "price": 150.0
            },
            {
              "available": true,
              "id": "26783191",
              "maxAmount": 1,
              "menuItemOptionId": 93947453,
              "minAmount": 0,
              "name": "Яблоки (35 г)",
              "price": 100.0
            },
            {
              "available": true,
              "id": "26783194",
              "maxAmount": 1,
              "menuItemOptionId": 93947458,
              "minAmount": 0,
              "name": "Сухофрукты (35 г)",
              "price": 100.0
            },
            {
              "available": true,
              "id": "26783197",
              "maxAmount": 1,
              "menuItemOptionId": 93947463,
              "minAmount": 0,
              "name": "Тыква в карамели (70 г)",
              "price": 100.0
            },
            {
              "available": true,
              "id": "26783200",
              "maxAmount": 1,
              "menuItemOptionId": 93947468,
              "minAmount": 0,
              "name": "Молоко сгущенное (80 г)",
              "price": 100.0
            }
          ],
          "name": "Начинки на выбор",
          "sortOrder": 100
        }
      ],
      "name": "Манная каша",
      "nutrients": {
        "calories": "666.66",
        "carbohydrates": "999.99",
        "fats": "888.88",
        "is_deactivated": true,
        "proteins": "777.77"
      },
      "price": 390.0,
      "sortOrder": 97,
      "vat": 0
    }
  ]
}
');

INSERT INTO eats_restapp_menu.menu_revisions(place_id, revision, origin, status, menu_hash)
VALUES (109151, 'MS4xNjA5NDU5MjAwMDAwLm44dUR3bkF4Q0tLYUxQLUxERG44Rnc', 'user_generated', 'applied', 'same_hash');
