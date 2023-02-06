#include <userver/formats/json.hpp>
#include <userver/utest/utest.hpp>

#include <merging/json_test_utils.hpp>
#include <merging/menu_json_diff.hpp>
#include <models/menu.hpp>
#include <parser/menu_parser.hpp>
#include <utils/menu_converter.hpp>

namespace {

const std::string kBase = R"--(
{
    "categories": [
        {
            "id": "103263",
            "parentId": null,
            "name": "Завтрак",
            "sortOrder": 130,
            "reactivatedAt": null,
            "available": true
        },
        {
            "id": "103265",
            "parentId": null,
            "name": "Закуски",
            "sortOrder": 160,
            "reactivatedAt": null,
            "available": true
        },
        {
            "id": "103279",
            "parentId": null,
            "name": "Детское меню",
            "sortOrder": 310,
            "reactivatedAt": null,
            "available": true
        }
    ],
    "items": [
        {
            "id": "1234583",
            "categoryId": "103263",
            "name": "Сухофрукты",
            "description": "",
            "price": 100,
            "vat": 0,
            "measure": 35,
            "measureUnit": "г",
            "sortOrder": 100,
            "modifierGroups": [],
            "images": [
                {
                    "hash": null,
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d9.jpeg"
                },
                {
                    "hash": null,
                    "url": "https://testing.eda.tst.yandex.net/images/1368744/9d2253f1d40f86ff4e525e998f49dfca.jpeg"
                }
            ],
            "thumbnails": [
                {
                    "hash": null,
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d9-80x80.jpeg"
                }
            ],
            "reactivatedAt": null,
            "available": true,
            "menuItemId": 37660163
        },
        {
            "id": "1234595",
            "categoryId": "103263",
            "name": "Сметана 20%",
            "description": "",
            "price": 100,
            "vat": 0,
            "measure": 50,
            "measureUnit": "г",
            "sortOrder": 100,
            "modifierGroups": [],
            "images": [
                {
                    "hash": null,
                    "url": "https://testing.eda.tst.yandex.net/images/1368744/9d2253f1d40f86ff4e525e998f49dfca.jpeg"
                }
            ],
            "thumbnails": [
                {
                    "hash": null,
                    "url": "https://testing.eda.tst.yandex.net/images/1368744/9d2253f1d40f86ff4e525e998f49dfca-80x80.jpeg"
                }
            ],
            "reactivatedAt": null,
            "available": true,
            "menuItemId": 37660168
        }
    ]
}
)--";

const std::string kBaseChangesInCategories = R"--(
{
    "categories": [
        {
            "id": "103263",
            "parentId": null,
            "name": "Завтракs",
            "sortOrder": 130,
            "reactivatedAt": null,
            "available": true
        },
        {
            "id": "103265",
            "parentId": null,
            "name": "Закуски",
            "sortOrder": 160,
            "reactivatedAt": null,
            "available": true
        },
        {
            "id": "103279",
            "parentId": null,
            "name": "Детское меню",
            "sortOrder": 310,
            "reactivatedAt": null,
            "available": true
        }
    ],
    "items": [
        {
            "id": "1234583",
            "categoryId": "103263",
            "name": "Сухофрукты",
            "description": "",
            "price": 100,
            "vat": 0,
            "measure": 35,
            "measureUnit": "г",
            "sortOrder": 100,
            "modifierGroups": [],
            "images": [
                {
                    "hash": null,
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d9.jpeg"
                },
                {
                    "hash": null,
                    "url": "https://testing.eda.tst.yandex.net/images/1368744/9d2253f1d40f86ff4e525e998f49dfca.jpeg"
                }
            ],
            "thumbnails": [
                {
                    "hash": null,
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d9-80x80.jpeg"
                }
            ],
            "reactivatedAt": null,
            "available": true,
            "menuItemId": 37660163
        },
        {
            "id": "1234595",
            "categoryId": "103263",
            "name": "Сметана 20%",
            "description": "",
            "price": 100,
            "vat": 0,
            "measure": 50,
            "measureUnit": "г",
            "sortOrder": 100,
            "modifierGroups": [],
            "images": [
                {
                    "hash": null,
                    "url": "https://testing.eda.tst.yandex.net/images/1368744/9d2253f1d40f86ff4e525e998f49dfca.jpeg"
                }
            ],
            "thumbnails": [
                {
                    "hash": null,
                    "url": "https://testing.eda.tst.yandex.net/images/1368744/9d2253f1d40f86ff4e525e998f49dfca-80x80.jpeg"
                }
            ],
            "reactivatedAt": null,
            "available": true,
            "menuItemId": 37660168
        }
    ]
}
)--";

const std::string kDeletedCategory = R"--(
{
    "categories": [
        {
            "id": "103265",
            "parentId": null,
            "name": "Закуски",
            "sortOrder": 160,
            "reactivatedAt": null,
            "available": null
        },
        {
            "id": "103279",
            "parentId": null,
            "name": "Детское меню",
            "sortOrder": 310,
            "reactivatedAt": null,
            "available": null
        }
    ],
    "items": [
        {
            "id": "1234583",
            "categoryId": "103263",
            "name": "Сухофрукты",
            "description": "",
            "price": 100,
            "vat": 0,
            "measure": 35,
            "measureUnit": "г",
            "sortOrder": 100,
            "modifierGroups": [],
            "images": [
                {
                    "hash": null,
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d9.jpeg"
                }
            ],
            "thumbnails": [
                {
                    "hash": null,
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d9-80x80.jpeg"
                }
            ],
            "reactivatedAt": null,
            "available": true,
            "menuItemId": 37660163
        },
        {
            "id": "554688",
            "categoryId": "103263",
            "name": "Сухофрукты",
            "description": "",
            "price": 100,
            "vat": 0,
            "measure": 35,
            "measureUnit": "г",
            "sortOrder": 100,
            "modifierGroups": [],
            "images": [
                {
                    "hash": null,
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d9.jpeg"
                }
            ],
            "thumbnails": [
                {
                    "hash": null,
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d9-80x80.jpeg"
                }
            ],
            "reactivatedAt": null,
            "available": true,
            "menuItemId": 37660163
        }
    ]
}
)--";

const std::string kExpected = R"--(
{
    "categories": [
        {
            "id": "103263",
            "op": "Rem"
        },
        {
            "id": "103265",
            "op": "Mod",
            "changed": {
                "available": null
            }
        },
        {
            "id": "103279",
            "op": "Mod",
            "changed": {
                "available": null
            }
        }
    ],
    "items": [
        {
            "id": "1234583",
            "op": "Mod",
            "changed": {
                "images": [
                    {
                        "hash": null,
                        "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d9.jpeg"
                    }
                ]
            }
        },
        {
            "id": "1234595",
            "op": "Rem"
        },
        {
            "id": "554688",
            "op": "Add",
            "changed": {
                "id": "554688",
                "categoryId": "103263",
                "name": "Сухофрукты",
                "description": "",
                "price": 100,
                "vat": 0,
                "measure": 35,
                "measureUnit": "г",
                "sortOrder": 100,
                "modifierGroups": [],
                "images": [
                    {
                        "hash": null,
                        "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d9.jpeg"
                    }
                ],
                "thumbnails": [
                    {
                        "hash": null,
                        "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d9-80x80.jpeg"
                    }
                ],
                "reactivatedAt": null,
                "available": true,
                "menuItemId": 37660163
            }
        }
    ]
}
)--";

const std::string kExpectedNoDiffInItems = R"--(
{
    "categories": [
        {
            "id": "103263",
            "op": "Mod",
            "changed": {
                "name": "Завтракs"
            }
        }
    ],
    "items": []
}
)--";

const std::string kEmptyDiff = R"--({"categories":[], "items":[]})--";

const std::string kExpectedCategories = R"--(
{
    "added": {},
    "changed": {
        "103279": {
            "available": null
        },
        "103265": {
            "available": null
        }
    },
    "removed": [
        "103263"
    ]
}
)--";

const std::string kExpectedItems = R"--(
{
    "added": {
        "554688": {
            "origin_id": "554688",
            "category_origin_ids":[
                "103263"
            ],
            "name": "Сухофрукты",
            "description": "",
            "price": "100",
            "vat": "0",
            "weight": {
                "value": "35",
                "unit": "г"
            },
            "sort": 100,
            "legacy_id": 37660163,
            "available": true,
            "reactivate_at": null,
            "pictures": [
                {
                    "avatarnica_identity": "1370147/36ca994761eb1fd00066ac634c96e0d9"
                }
            ],
            "options_groups": []
        }
    },
    "changed": {
        "1234583": {
            "pictures": [
                {
                    "avatarnica_identity": "1370147/36ca994761eb1fd00066ac634c96e0d9"
                }
            ]
        }
    },
    "removed": [
        "1234595"
    ]
}
)--";

const std::string kExpectedNoDiffItems = R"--(
{
    "added": {},
    "changed": {
        "103263": {
            "name": "Завтракs"
        }
    },
    "removed": []
}
)--";

const std::string kExpectedEmpty = R"--(
{
    "added": {},
    "changed": {},
    "removed": []
}
)--";

std::pair<eats_restapp_menu::models::MenuCategoriesMap,
          eats_restapp_menu::models::MenuItemsMap>
PrepareMenu(const std::string& menu_json) {
  auto json = eats_restapp_menu::utils::MenuConvertV1ToV2(
      formats::json::FromString(menu_json));

  std::vector<::formats::json::Value> categories_vec, items_vec;
  for (const auto category :
       json[eats_restapp_menu::merging::kJsonPathCategories]) {
    categories_vec.emplace_back(std::move(category));
  }
  for (const auto item : json[eats_restapp_menu::merging::kJsonPathItems]) {
    items_vec.emplace_back(std::move(item));
  }

  auto categories =
      eats_restapp_menu::parser::ParseMenuCategories(std::move(categories_vec));
  auto items = eats_restapp_menu::parser::ParseMenuItems(std::move(items_vec));

  return {categories, items};
}

std::pair<eats_restapp_menu::models::MenuCategoriesMap,
          eats_restapp_menu::models::MenuItemsMap>
PrepareMenuV2(const std::string& menu_json) {
  auto json = formats::json::FromString(menu_json);

  std::vector<::formats::json::Value> categories_vec, items_vec;
  for (const auto category :
       json[eats_restapp_menu::merging::kJsonPathCategories]) {
    categories_vec.emplace_back(std::move(category));
  }
  for (const auto item : json[eats_restapp_menu::merging::kJsonPathItems]) {
    items_vec.emplace_back(std::move(item));
  }

  auto categories =
      eats_restapp_menu::parser::ParseMenuCategories(std::move(categories_vec));
  auto items = eats_restapp_menu::parser::ParseMenuItems(std::move(items_vec));

  return {categories, items};
}

}  // namespace

namespace eats_restapp_menu::merging::tests {

TEST(CalculateDiff, Develop) {
  std::string first =
      R"--(
{"id": "kbjncrhr-o7k6r7kprbr-9sqydbly539",
      "name": "Дополнительно" }
)--";

  std::string second =
      R"--(
{"name": "Дополнительно",
"id": "kbjncrhr-o7k6r7kprbr-9sqydbly539"
       }
)--";
  ASSERT_EQ(formats::json::FromString(first),
            formats::json::FromString(second));
}

TEST(CalculateDiff, Basic) {
  JsonMenuDifferencer differencer;

  const auto& first = formats::json::FromString(kBase);
  const auto& second = formats::json::FromString(kDeletedCategory);

  const auto& diff = differencer.GetMenuJsonDiff(Menu{first}, Menu{second});

  ASSERT_TRUE(CheckJsonEquals(diff.GetUnderlying(),
                              formats::json::FromString(kExpected)));
}

TEST(CalculateDiff, NoDiffInItems) {
  JsonMenuDifferencer differencer;

  const auto& first = formats::json::FromString(kBase);
  const auto& second = formats::json::FromString(kBaseChangesInCategories);

  const auto& diff = differencer.GetMenuJsonDiff(Menu{first}, Menu{second});

  ASSERT_TRUE(CheckJsonEquals(
      diff.GetUnderlying(), formats::json::FromString(kExpectedNoDiffInItems)));
}

TEST(CalculateDiff, Empty) {
  JsonMenuDifferencer differencer;

  const auto& first = formats::json::FromString(kBase);
  const auto& second = formats::json::FromString(kBase);

  const auto& diff = differencer.GetMenuJsonDiff(Menu{first}, Menu{second});

  ASSERT_TRUE(CheckJsonEquals(diff.GetUnderlying(),
                              formats::json::FromString(kEmptyDiff)));
}

TEST(CalculateDiff, Basic_new) {
  JsonMenuDifferencer differencer;

  auto [first_categories, first_items] = PrepareMenu(kBase);
  auto [second_categories, second_items] = PrepareMenu(kDeletedCategory);

  const auto& diff_categories =
      differencer.GetMenuCategoriesDiff(first_categories, second_categories);
  const auto& diff_items =
      differencer.GetMenuItemsDiff(first_items, second_items);

  ASSERT_EQ(formats::json::ValueBuilder{diff_categories}.ExtractValue(),
            formats::json::FromString(kExpectedCategories));
  ASSERT_EQ(formats::json::ValueBuilder{diff_items}.ExtractValue(),
            formats::json::FromString(kExpectedItems));
}

TEST(CalculateDiff, NoDiffInItems_new) {
  JsonMenuDifferencer differencer;

  auto [first_categories, first_items] = PrepareMenu(kBase);
  auto [second_categories, second_items] =
      PrepareMenu(kBaseChangesInCategories);

  const auto& diff_categories =
      differencer.GetMenuCategoriesDiff(first_categories, second_categories);
  const auto& diff_items =
      differencer.GetMenuItemsDiff(first_items, second_items);

  ASSERT_EQ(formats::json::ValueBuilder{diff_categories}.ExtractValue(),
            formats::json::FromString(kExpectedNoDiffItems));
  ASSERT_EQ(formats::json::ValueBuilder{diff_items}.ExtractValue(),
            formats::json::FromString(kExpectedEmpty));
}

TEST(CalculateDiff, Empty_new) {
  JsonMenuDifferencer differencer;

  auto [first_categories, first_items] = PrepareMenu(kBase);
  auto [second_categories, second_items] = PrepareMenu(kBase);

  const auto& diff_categories =
      differencer.GetMenuCategoriesDiff(first_categories, second_categories);
  const auto& diff_items =
      differencer.GetMenuItemsDiff(first_items, second_items);

  ASSERT_EQ(formats::json::ValueBuilder{diff_categories}.ExtractValue(),
            formats::json::FromString(kExpectedEmpty));
  ASSERT_EQ(formats::json::ValueBuilder{diff_items}.ExtractValue(),
            formats::json::FromString(kExpectedEmpty));
}

const std::string kModifiers1 = R"--(
{
    "categories": [
        {
            "id": "103263",
            "parentId": null,
            "name": "Завтрак",
            "sortOrder": 130,
            "reactivatedAt": null,
            "available": true
        },
        {
            "id": "103265",
            "parentId": null,
            "name": "Закуски",
            "sortOrder": 160,
            "reactivatedAt": null,
            "available": true
        },
        {
            "id": "103279",
            "parentId": null,
            "name": "Детское меню",
            "sortOrder": 310,
            "reactivatedAt": null,
            "available": true
        }
    ],
    "items": [
        {
            "options_groups":
            [
                {
                    "origin_id": "kyir6454-n5nakpixm8q-46t8xtgqglj",
                    "options": [
                        {
                            "name": "1",
                            "origin_id": "kyir6bk0-yrjx3biv35-q6qfhft87ll",
                            "price": "1",
                            "min_amount": 0,
                            "max_amount": 1,
                            "available": true,
                            "sort": 100,
                            "multiplier": 1
                        },
                        {
                            "name": "2",
                            "origin_id": "kyir6ft8-qbxn0ji0nrb-b8rcidfh19n",
                            "price": "2",
                            "min_amount": 0,
                            "max_amount": 1,
                            "available": true,
                            "sort": 100,
                            "multiplier": 1
                        },
                        {
                            "name": "3",
                            "origin_id": "kyir6j3a-h4vn7wvsfp-4amgulv16gg",
                            "price": "3",
                            "min_amount": 0,
                            "max_amount": 1,
                            "available": true,
                            "sort": 100,
                            "multiplier": 1
                        }
                    ],
                    "name": "Обязалово",
                    "min_selected_options": 1,
                    "max_selected_options": 1,
                    "sort": 100,
                    "is_required": true
                }
            ],
            "name":"Сио Рамен (изменен)",
            "description":"Лёгкий шестичасовой бульон на свинине и курице, лапша, курица, менма, красный лук, зелёный лук, нори, лимон",
            "weight":{"value":"600","unit":"г"},

            "origin_id":"11727404",
            "category_origin_ids":["947816"],
            "price":"500",
            "vat":"-1",
            "sort":100,
            "shipping_types":["delivery","pickup"],
            "choosable":true,
            "available":false,
            "legacy_id":11727404,
            "adult":false,
            "ordinary":false,
            "pictures":
            [
                {
                    "avatarnica_identity":"1370147/7615a44d425fd5cefa219e61ce11259d",
                    "url":"https://testing.eda.tst.yandex.net/images/1370147/7615a44d425fd5cefa219e61ce11259d.jpeg"
                }
            ]
        }
    ]
}
)--";

TEST(CalculateDiff, Modifiers) {
  JsonMenuDifferencer differencer;

  auto [first_categories, first_items] = PrepareMenuV2(kModifiers1);
  auto [second_categories, second_items] = PrepareMenuV2(kModifiers1);

  const auto& diff_categories =
      differencer.GetMenuCategoriesDiff(first_categories, second_categories);
  const auto& diff_items =
      differencer.GetMenuItemsDiff(first_items, second_items);

  ASSERT_EQ(formats::json::ValueBuilder{diff_categories}.ExtractValue(),
            formats::json::FromString(kExpectedEmpty));
  ASSERT_EQ(formats::json::ValueBuilder{diff_items}.ExtractValue(),
            formats::json::FromString(kExpectedEmpty));
}

}  // namespace eats_restapp_menu::merging::tests
