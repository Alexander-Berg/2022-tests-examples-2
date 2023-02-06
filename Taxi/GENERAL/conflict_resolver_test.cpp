#include <userver/formats/json.hpp>
#include <userver/utest/utest.hpp>

#include <merging/conflict_resolver.hpp>

namespace {

const std::string kConflicts = R"--(
{
    "categories": [],
    "items": [
        {
            "id": "554688",
            "op1": "Add",
            "op2": "Add",
            "changed1": {
                "name": "Сухофрукты",
                "measure": 40
            },
            "changed2": {
                "name": "Сухофруктs",
                "measure": 35
            }
        }
    ]
}
)--";

const std::string kFreeDiff = R"--(
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
            "op": "Mod",
            "changed": {
                "available": null
            }
        }
    ],
    "items": [
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
                "menuItemId": 37660163
            }
        }
    ]
}
)--";

const std::string kNoConflicts = R"--(
{
    "categories": [
        {
            "id": "103263",
            "op": "Rem"
        },
        {
            "id": "42345",
            "op": "Rem"
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
        },
        {
            "id": "103263",
            "op": "Rem"
        },
        {
            "id": "42345",
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

const std::string kEmptyDiff = R"--({"categories":[], "items":[]})--";

const std::string kExpectedWithEmptyDiff = R"--(
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
            "op": "Mod",
            "changed": {
                "available": null
            }
        },
        {
            "id": "103263",
            "op": "Rem"
        },
        {
            "id": "42345",
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
                "menuItemId": 37660163
            }
        },
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

const std::string kOnlyConflictsExpected = R"--(
{
    "categories": [],
    "items": [
        {
            "id": "554688",
            "op": "Add",
            "changed": {
                "name": "Сухофрукты",
                "measure": 40
            }
        }
    ]
}
)--";

const std::string kNoConflictFreeExpected = R"--(
{
    "categories": [
        {
            "id": "103263",
            "op": "Rem"
        },
        {
            "id": "42345",
            "op": "Rem"
        }
    ],
    "items": [
        {
            "id": "554688",
            "op": "Add",
            "changed": {
                "name": "Сухофрукты",
                "measure": 40
            }
        },
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

const std::string kOnlyConflictsAndFreeExpected = R"--(
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
            "op": "Mod",
            "changed": {
                "available": null
            }
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
        }
    ]
}
)--";
}  // namespace

namespace eats_restapp_menu::merging::tests {
TEST(ConflictResolver, Base) {
  ConflictResolver resolver{MakeFirstJsonResolveStrategy()};

  auto result = resolver.Resolve(
      Conflicts{formats::json::FromString(kConflicts)},
      DiffWithSameChanges{formats::json::FromString(kFreeDiff)},
      DiffWithoutConflicts{formats::json::FromString(kNoConflicts)});

  ASSERT_EQ(result.GetUnderlying(), formats::json::FromString(kExpected));
}

TEST(ConflictResolver, NoConflict) {
  ConflictResolver resolver{MakeFirstJsonResolveStrategy()};

  auto result = resolver.Resolve(
      Conflicts{formats::json::FromString(kEmptyDiff)},
      DiffWithSameChanges{formats::json::FromString(kFreeDiff)},
      DiffWithoutConflicts{formats::json::FromString(kNoConflicts)});

  ASSERT_EQ(result.GetUnderlying(),
            formats::json::FromString(kExpectedWithEmptyDiff));
}

TEST(ConflictResolver, OnlyConflict) {
  ConflictResolver resolver{MakeFirstJsonResolveStrategy()};

  auto result = resolver.Resolve(
      Conflicts{formats::json::FromString(kConflicts)},
      DiffWithSameChanges{formats::json::FromString(kEmptyDiff)},
      DiffWithoutConflicts{formats::json::FromString(kEmptyDiff)});

  ASSERT_EQ(result.GetUnderlying(),
            formats::json::FromString(kOnlyConflictsExpected));
}

TEST(ConflictResolver, NoConflictFree) {
  ConflictResolver resolver{MakeFirstJsonResolveStrategy()};

  auto result = resolver.Resolve(
      Conflicts{formats::json::FromString(kConflicts)},
      DiffWithSameChanges{formats::json::FromString(kEmptyDiff)},
      DiffWithoutConflicts{formats::json::FromString(kNoConflicts)});

  ASSERT_EQ(result.GetUnderlying(),
            formats::json::FromString(kNoConflictFreeExpected));
}

TEST(ConflictResolver, NoConflictNoFree) {
  ConflictResolver resolver{MakeFirstJsonResolveStrategy()};

  auto result = resolver.Resolve(
      Conflicts{formats::json::FromString(kEmptyDiff)},
      DiffWithSameChanges{formats::json::FromString(kEmptyDiff)},
      DiffWithoutConflicts{formats::json::FromString(kNoConflicts)});

  ASSERT_EQ(result.GetUnderlying(), formats::json::FromString(kNoConflicts));
}

TEST(ConflictResolver, OnlyConflictsAndFree) {
  ConflictResolver resolver{MakeFirstJsonResolveStrategy()};

  auto result = resolver.Resolve(
      Conflicts{formats::json::FromString(kConflicts)},
      DiffWithSameChanges{formats::json::FromString(kFreeDiff)},
      DiffWithoutConflicts{formats::json::FromString(kEmptyDiff)});

  ASSERT_EQ(result.GetUnderlying(),
            formats::json::FromString(kOnlyConflictsAndFreeExpected));
}

}  // namespace eats_restapp_menu::merging::tests
