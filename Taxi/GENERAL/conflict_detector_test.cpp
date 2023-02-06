#include <userver/formats/json.hpp>
#include <userver/utest/utest.hpp>

#include <merging/conflict_detector.hpp>

#include "json_test_utils.hpp"

namespace {

const std::string kHighPriorityConflictDiff = R"--(
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
                "name": "Сухофрукты",
                "description": "",
                "price": 100,
                "vat": 0,
                "measure": 40,
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

const std::string kLowPriorityConflictDiff = R"--(
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
                "available": "1"
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
                "name": "Сухофруктs",
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

const std::string kLowPriorityConflictDiff2 = R"--(
{
    "categories": [
    ],
    "items": [
    ]
}
)--";

const std::string kExpectedConflicts = R"--(
{
    "categories": [
        {
            "id": "103279",
            "op1": "Mod",
            "op2": "Mod",
            "changed1": {
                "available": null
            },
            "changed2": {
                "available": "1"
            }
        }
    ],
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

const std::string kExpectedDiffWithSameChanges = R"--(
{
    "categories": [
        {
            "id": "103265",
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

const std::string kExpectedConflictsWithCustomRule = R"--(
{
    "categories": [],
    "items": [
        {
            "id": "554688",
            "op1": "Add",
            "op2": "Add",
            "changed1": {
                "name": "Сухофрукты",
                "price": 100,
                "measure": 40
            },
            "changed2": {
                "name": "Сухофруктs",
                "price": 100,
                "measure": 35
            }
        }
    ]
}
)--";

const std::string kExpectedDiffWithSameChangesWithCustomRule = R"--(
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

const std::string kEmptyDiff = R"--({"categories":[], "items":[]})--";

const std::string kExpectedItemsConflicts = R"--(
{
    "conflicts": {
        "554688": {
            "op1": "added",
            "op2": "added",
            "changed1": {
                "name": "Сухофрукты",
                "measure": 40
            },
            "changed2": {
                "name": "Сухофруктs",
                "measure": 35
            },
            "options_changed1": null,
            "options_changed2": null
        }
    },
    "no_conflicts": {
        "1234595": {
            "op": "removed",
            "changed": null,
            "options_changed": null
        },
        "554688": {
            "op": "added",
            "changed": {
                "id": "554688",
                "categoryId": "103263",
                "description": "",
                "price": 100,
                "vat": 0,
                "measureUnit": "г",
                "sortOrder": 100,
                "menuItemId": 37660163,
                "available": true,
                "reactivatedAt": null,
                "images": [
                    {
                        "identity": "1370147/36ca994761eb1fd00066ac634c96e0d9"
                    }
                ],
                "modifierGroups": []
            },
            "options_changed": null
        }
    }
}
)--";

const std::string kExpectedItemsConflictsCustomRule = R"--(
{
    "conflicts": {
        "554688": {
            "op1": "added",
            "op2": "added",
            "changed1": {
                "name": "Сухофрукты",
                "price": 100,
                "measure": 40
            },
            "changed2": {
                "name": "Сухофруктs",
                "price": 100,
                "measure": 35
            },
            "options_changed1": null,
            "options_changed2": null
        }
    },
    "no_conflicts": {
        "1234595": {
            "op": "removed",
            "changed": null,
            "options_changed": null
        },
        "554688": {
            "op": "added",
            "changed": {
                "id": "554688",
                "categoryId": "103263",
                "description": "",
                "vat": 0,
                "measureUnit": "г",
                "sortOrder": 100,
                "menuItemId": 37660163,
                "available": true,
                "reactivatedAt": null,
                "images": [
                    {
                        "identity": "1370147/36ca994761eb1fd00066ac634c96e0d9"
                    }
                ],
                "modifierGroups": []
            },
            "options_changed": null
        }
    }
}
)--";

const std::string kExpectedCategoriesConflicts = R"--(
{
    "conflicts": {
        "103279": {
            "op1": "changed",
            "op2": "changed",
            "changed1": {
                "available": null
            },
            "changed2": {
                "available": "1"
            }
        }
    },
    "no_conflicts": {
        "103265": {
            "op": "changed",
            "changed": {
                "available": null
            }
        }
    }
}
)--";

const std::string kExpectedCategoriesConflictsCustomRule = R"--(
{
    "conflicts": {},
    "no_conflicts": {
        "103279": {
            "op": "changed",
            "changed": {
                "available": null
            }
        },
        "103265": {
            "op": "changed",
            "changed": {
                "available": null
            }
        }
    }
}
)--";

const std::string kHighPriorityItemsDiff = R"--(
{
    "added": {
        "554688": {
            "id": "554688",
            "categoryId": "103263",
            "name": "Сухофрукты",
            "description": "",
            "price": 100,
            "vat": 0,
            "measure": 40,
            "measureUnit": "г",
            "sortOrder": 100,
            "menuItemId": 37660163,
            "available": true,
            "reactivatedAt": null,
            "images": [
                {
                    "identity": "1370147/36ca994761eb1fd00066ac634c96e0d9"
                }
            ],
            "modifierGroups": []
        }
    },
    "removed": [
        "1234595"
    ]
}
)--";

const std::string kLowPriorityItemsDiff = R"--(
{
    "added": {
        "554688": {
            "id": "554688",
            "categoryId": "103263",
            "name": "Сухофруктs",
            "description": "",
            "price": 100,
            "vat": 0,
            "measure": 35,
            "measureUnit": "г",
            "sortOrder": 100,
            "menuItemId": 37660163,
            "available": true,
            "reactivatedAt": null,
            "images": [
                {
                    "identity": "1370147/36ca994761eb1fd00066ac634c96e0d9"
                }
            ],
            "modifierGroups": []
        }
    },
    "removed": [
        "1234595"
    ]
}
)--";

const std::string kLowPriorityItemsDiff2 = R"--(
{
}
)--";

const std::string kHighPriorityCategoriesDiff = R"--(
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
    "removed": []
}
)--";

const std::string kLowPriorityCategoriesDiff = R"--(
{
    "changed": {
        "103279": {
            "available": "1"
        },
        "103265": {
            "available": null
        }
    }
}
)--";

const std::string kExpectedSameChanges = R"--(
{
    "conflicts": {},
    "no_conflicts": {}
}
)--";

const std::string kEmptyChangesDiff = "{}";

class CustomItemTestRule final
    : public eats_restapp_menu::merging::ConflictDetectorRuleBase {
 public:
  CustomItemTestRule()
      : eats_restapp_menu::merging::ConflictDetectorRuleBase("price") {}
  ~CustomItemTestRule() = default;
  bool CheckRule(
      [[maybe_unused]] const eats_restapp_menu::merging::JsonVal& high_priority,
      [[maybe_unused]] const eats_restapp_menu::merging::JsonVal& low_priority)
      const override {
    return true;
  }
};

class CustomCategoryTestRule final
    : public eats_restapp_menu::merging::ConflictDetectorRuleBase {
 public:
  CustomCategoryTestRule()
      : eats_restapp_menu::merging::ConflictDetectorRuleBase("available") {}
  ~CustomCategoryTestRule() = default;
  bool CheckRule(
      [[maybe_unused]] const eats_restapp_menu::merging::JsonVal& high_priority,
      [[maybe_unused]] const eats_restapp_menu::merging::JsonVal& low_priority)
      const override {
    return false;
  }
};

std::unique_ptr<eats_restapp_menu::merging::ConflictDetectorRuleBase>
MakeDefaultCategoryRule() {
  return std::make_unique<CustomCategoryTestRule>();
}

std::unique_ptr<eats_restapp_menu::merging::ConflictDetectorRuleBase>
MakeDefaultItemRule() {
  return std::make_unique<CustomItemTestRule>();
}

}  // namespace

namespace eats_restapp_menu::merging::tests {

TEST(ConflictDetector, Basic) {
  ConflictDetector detector;
  auto result = detector.DetectConflicts(
      MenuDiff{formats::json::FromString(kHighPriorityConflictDiff)},
      MenuDiff{formats::json::FromString(kLowPriorityConflictDiff)});

  ASSERT_TRUE(CheckJsonEquals(UnderlyingValue(result.conflicts),
                              formats::json::FromString(kExpectedConflicts)));
  ASSERT_TRUE(
      CheckJsonEquals(UnderlyingValue(result.diff_with_same_changes),
                      formats::json::FromString(kExpectedDiffWithSameChanges)));
}

TEST(ConflictDetector, CustomRule) {
  ConflictDetector detector;
  detector.RegisterRuleForCategories(MakeDefaultCategoryRule());
  detector.RegisterRuleForItems(MakeDefaultItemRule());

  auto result = detector.DetectConflicts(
      MenuDiff{formats::json::FromString(kHighPriorityConflictDiff)},
      MenuDiff{formats::json::FromString(kLowPriorityConflictDiff)});

  ASSERT_TRUE(CheckJsonEquals(
      UnderlyingValue(result.conflicts),
      formats::json::FromString(kExpectedConflictsWithCustomRule)));
  ASSERT_TRUE(CheckJsonEquals(
      UnderlyingValue(result.diff_with_same_changes),
      formats::json::FromString(kExpectedDiffWithSameChangesWithCustomRule)));
}

TEST(ConflictDetector, EmptyIn) {
  ConflictDetector detector;
  detector.RegisterRuleForCategories(MakeDefaultCategoryRule());
  detector.RegisterRuleForItems(MakeDefaultItemRule());

  auto result =
      detector.DetectConflicts(MenuDiff{formats::json::FromString(kEmptyDiff)},
                               MenuDiff{formats::json::FromString(kEmptyDiff)});

  ASSERT_TRUE(CheckJsonEquals(UnderlyingValue(result.conflicts),
                              formats::json::FromString(kEmptyDiff)));
  ASSERT_TRUE(CheckJsonEquals(UnderlyingValue(result.diff_with_same_changes),
                              formats::json::FromString(kEmptyDiff)));
}

TEST(ConflictDetector, Basic_new) {
  ConflictDetector detector;

  auto high_items =
      formats::json::FromString(kHighPriorityItemsDiff).As<ItemsDiff>();
  auto low_items =
      formats::json::FromString(kLowPriorityItemsDiff).As<ItemsDiff>();
  auto high_categories = formats::json::FromString(kHighPriorityCategoriesDiff)
                             .As<CategoriesDiff>();
  auto low_categories = formats::json::FromString(kLowPriorityCategoriesDiff)
                            .As<CategoriesDiff>();

  auto res_items = detector.DetectItemConflicts(high_items, low_items);
  auto res_categories =
      detector.DetectCategoryConflicts(high_categories, low_categories);

  ASSERT_EQ(
      Serialize(res_items, formats::serialize::To<::formats::json::Value>{}),
      formats::json::FromString(kExpectedItemsConflicts));
  ASSERT_EQ(Serialize(res_categories,
                      formats::serialize::To<::formats::json::Value>{}),
            formats::json::FromString(kExpectedCategoriesConflicts));
}

TEST(ConflictDetector, CustomRule_new) {
  ConflictDetector detector;
  detector.RegisterRuleForCategories(MakeDefaultCategoryRule());
  detector.RegisterRuleForItems(MakeDefaultItemRule());

  auto high_items =
      formats::json::FromString(kHighPriorityItemsDiff).As<ItemsDiff>();
  auto low_items =
      formats::json::FromString(kLowPriorityItemsDiff).As<ItemsDiff>();
  auto high_categories = formats::json::FromString(kHighPriorityCategoriesDiff)
                             .As<CategoriesDiff>();
  auto low_categories = formats::json::FromString(kLowPriorityCategoriesDiff)
                            .As<CategoriesDiff>();

  auto res_items = detector.DetectItemConflicts(high_items, low_items);
  auto res_categories =
      detector.DetectCategoryConflicts(high_categories, low_categories);

  ASSERT_EQ(
      Serialize(res_items, formats::serialize::To<::formats::json::Value>{}),
      formats::json::FromString(kExpectedItemsConflictsCustomRule));
  ASSERT_EQ(Serialize(res_categories,
                      formats::serialize::To<::formats::json::Value>{}),
            formats::json::FromString(kExpectedCategoriesConflictsCustomRule));
}

TEST(ConflictDetector, EmptyIn_new) {
  ConflictDetector detector;
  detector.RegisterRuleForCategories(MakeDefaultCategoryRule());
  detector.RegisterRuleForItems(MakeDefaultItemRule());

  auto high_items =
      formats::json::FromString(kEmptyChangesDiff).As<ItemsDiff>();
  auto high_categories =
      formats::json::FromString(kEmptyChangesDiff).As<CategoriesDiff>();

  auto res_items = detector.DetectItemConflicts(high_items, high_items);
  auto res_categories =
      detector.DetectCategoryConflicts(high_categories, high_categories);

  ASSERT_EQ(
      Serialize(res_items, formats::serialize::To<::formats::json::Value>{}),
      formats::json::FromString(kExpectedSameChanges));
  ASSERT_EQ(Serialize(res_categories,
                      formats::serialize::To<::formats::json::Value>{}),
            formats::json::FromString(kExpectedSameChanges));
}

}  // namespace eats_restapp_menu::merging::tests
