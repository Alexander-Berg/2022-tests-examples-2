#include <userver/formats/json.hpp>
#include <userver/utest/utest.hpp>

#include <merging/diff_merger.hpp>

#include "json_test_utils.hpp"

namespace {

const std::string kMenu = R"--(
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
        },
        {
            "id": "12345553",
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
        }
    ]
}
)--";

const std::string kDiff = R"--(
{
    "categories": [
        {
            "id": "103265",
            "op": "Mod",
            "changed": {
                "available": null
            }
        },
        {
            "id": "103279",
            "op": "Add",
            "changed": {
                "id": "103279",
                "parentId": null,
                "name": "Закусon",
                "sortOrder": 777,
                "reactivatedAt": null,
                "available": true
            }
        },
        {
            "id": "103263",
            "op": "Rem"
        }
    ],
    "items": [
        {
            "id": "554688",
            "op": "Add",
            "changed": {
                "id": "554688",
                "categoryId": "103263",
                "description": "",
                "price": 100,
                "vat": 0,
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
                "menuItemId": 37660163,
                "name": "Сухофрукты",
                "measure": 40
            }
        },
        {
            "id": "1234583",
            "op": "Rem"
        },
        {
            "id": "12345553",
            "op": "Mod",
            "changed": {
                "images": [
                    {
                        "hash": null,
                        "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d9.jpeg"
                    }
                ]
            }
        }
    ]
}
)--";

const std::string kExpected = R"--(
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
            "name": "Закусon",
            "sortOrder": 777,
            "reactivatedAt": null,
            "available": true
        }
    ],
    "items": [
        {
            "id": "12345553",
            "categoryId": "103263",
            "name": "Сухофрукты",
            "description": "",
            "price": 100,
            "vat": 0,
            "measure": 35,
            "measureUnit": "г",
            "sortOrder": 100,
            "modifierGroups": [],
            "thumbnails": [
                {
                    "hash": null,
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d9-80x80.jpeg"
                }
            ],
            "reactivatedAt": null,
            "available": true,
            "menuItemId": 37660163,
            "images": [
                {
                    "hash": null,
                    "url": "https://testing.eda.tst.yandex.net/images/1370147/36ca994761eb1fd00066ac634c96e0d9.jpeg"
                }
            ]
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
        },
        {
            "id": "554688",
            "categoryId": "103263",
            "description": "",
            "price": 100,
            "vat": 0,
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
            "menuItemId": 37660163,
            "name": "Сухофрукты",
            "measure": 40
        }
    ]
}
)--";

const std::string kEmptyDiff = R"--({"categories":[], "items":[]})--";

const std::string kEmptyItemsDiff = R"--(
{
    "categories": [
        {
            "id": "103265",
            "op": "Mod",
            "changed": {
                "available": null
            }
        },
        {
            "id": "103279",
            "op": "Add",
            "changed": {
                "id": "103279",
                "parentId": null,
                "name": "Закусon",
                "sortOrder": 777,
                "reactivatedAt": null,
                "available": true
            }
        },
        {
            "id": "103263",
            "op": "Rem"
        }
    ],
    "items": []
}
)--";

const std::string kEmptyItemsDiffExpected = R"--(
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
            "name": "Закусon",
            "sortOrder": 777,
            "reactivatedAt": null,
            "available": true
        }
    ],
    "items": [
        {
            "id": "12345553",
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

}  // namespace

namespace eats_restapp_menu::merging::tests {

TEST(Merger, Base) {
  auto result = MenuMerger().Merge(Menu{formats::json::FromString(kMenu)},
                                   MenuDiff{formats::json::FromString(kDiff)});

  ASSERT_TRUE(CheckJsonEquals(result.GetUnderlying(),
                              formats::json::FromString(kExpected)));
}

TEST(Merger, EmptyDiff) {
  auto result =
      MenuMerger().Merge(Menu{formats::json::FromString(kMenu)},
                         MenuDiff{formats::json::FromString(kEmptyDiff)});

  ASSERT_TRUE(CheckJsonEquals(result.GetUnderlying(),
                              formats::json::FromString(kMenu)));
}

TEST(Merger, EmptyItems) {
  auto result =
      MenuMerger().Merge(Menu{formats::json::FromString(kMenu)},
                         MenuDiff{formats::json::FromString(kEmptyItemsDiff)});

  ASSERT_TRUE(
      CheckJsonEquals(result.GetUnderlying(),
                      formats::json::FromString(kEmptyItemsDiffExpected)));
}

}  // namespace eats_restapp_menu::merging::tests
