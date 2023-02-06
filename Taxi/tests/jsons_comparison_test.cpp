#include <gtest/gtest.h>

#include <utils/helpers/json.hpp>
#include <utils/helpers/params.hpp>
#include <utils/jsons_comparison.hpp>

namespace {
namespace ujc = utils::jsons_comparison;

Json::Value ReadJson(const std::string& json) {
  Json::Value doc;
  if (!utils::helpers::TryParseJson(json, doc, {})) {
    throw utils::helpers::JsonMemberTypeError("Failed to parse json ");
  }
  return doc;
}

static constexpr auto kSubventionsStatusExample1 = R"JSON({
  "subventions_status": [
    {
      "are_restrictions_satisfied": true,
      "description": {
        "subtitle": "498 ₽ за 60 мин",
        "title": "Гарантия"
      },
      "description_items": [
        {
          "type": "title"
        },
        {
          "accent": true,
          "detail": "4 ч 26 мин",
          "title": "Ваше время в синей зоне",
          "type": "detail"
        },
        {
          "accent": true,
          "detail": "8 ч",
          "title": "Минимальное время",
          "type": "detail"
        },
        {
          "accent": true,
          "detail": "1319 ₽",
          "title": "Заработок за заказы",
          "type": "detail"
        },
        {
          "accent": true,
          "detail": "0 ₽",
          "title": "Бонус",
          "type": "detail"
        },
        {
          "title": "Требования",
          "type": "title"
        },
        {
          "left_tip": {
            "background_color": "#F1F0ED",
            "form": "round",
            "icon": {
              "icon_type": "check",
              "tint_color": "#0596FA"
            }
          },
          "subtitle": "У вас 99",
          "title": "Активность не ниже 70",
          "type": "tip_detail"
        },
        {
          "left_tip": {
            "background_color": "#F1F0ED",
            "form": "round",
            "icon": {
              "icon_type": "check",
              "tint_color": "#0596FA"
            }
          },
          "subtitle": "У вас: Любой",
          "title": "Способ оплаты Любой",
          "type": "tip_detail"
        },
        {
          "left_tip": {
            "background_color": "#F1F0ED",
            "form": "round",
            "icon": {
              "icon_type": "check",
              "tint_color": "#0596FA"
            }
          },
          "subtitle": "Вы в синей зоне ",
          "title": "Нахождение в синей зоне",
          "type": "tip_detail"
        },
        {
          "left_tip": {
            "background_color": "#F1F0ED",
            "form": "round",
            "icon": {
              "icon_type": "check",
              "tint_color": "#0596FA"
            }
          },
          "subtitle": "У вас Эконом, UberX, Специальный",
          "title": "Эконом, UberX, Специальный",
          "type": "tip_detail"
        }
      ],
      "geoareas": [
        {
          "id": "71b7eb1434ed42a99b101c40bdd2c8e7",
          "is_in_area": true
        }
      ],
      "id": "_id/5e4ac31d8fe28d5ce4be0dab",
      "toolbar_item": {
        "left_tip": {
          "background_color": "#0596FA",
          "form": "round",
          "icon": {
            "icon_type": "time",
            "tint_color": "#FFFFFF"
          },
          "size": "mu_6"
        },
        "primary_max_lines": 1,
        "primary_text_size": "title_small",
        "reverse": true,
        "secondary_text_color": "#0596FA",
        "subtitle": "4 ч 26 мин",
        "title": "Вы в синей зоне ",
        "type": "tip_detail"
      }
    },
    {
      "are_restrictions_satisfied": true,
      "description_items": [
        {
          "type": "title"
        },
        {
          "title": "Требования",
          "type": "title"
        },
        {
          "left_tip": {
            "background_color": "#F1F0ED",
            "form": "round",
            "icon": {
              "icon_type": "check",
              "tint_color": "#0596FA"
            }
          },
          "subtitle": "У вас Специальный",
          "title": "Специальный",
          "type": "tip_detail"
        }
      ],
      "id": "_id/5d551edcc081365f035eaed3"
    }
  ]
})JSON";

static constexpr auto kSubventionsStatusExample2 = R"JSON({
  "subventions_status": [
    {
      "are_restrictions_satisfied": true,
      "description": {
        "subtitle": "498 ₽ за 60 мин",
        "title": "Гарантия"
      },
      "description_items": [
        {
          "type": "title"
        },
        {
          "accent": true,
          "detail": "4 ч 26 мин",
          "title": "Ваше время в синей зоне",
          "type": "detail"
        },
        {
          "accent": true,
          "detail": "8 ч",
          "title": "Минимальное время",
          "type": "detail"
        },
        {
          "accent": true,
          "detail": "1319 ₽",
          "title": "Заработок за заказы",
          "type": "detail"
        },
        {
          "accent": true,
          "detail": "0 ₽",
          "title": "Бонус",
          "type": "detail"
        },
        {
          "title": "Требования",
          "type": "title"
        },
        {
          "left_tip": {
            "background_color": "#F1F0ED",
            "form": "round",
            "icon": {
              "icon_type": "check",
              "tint_color": "#0596FB"
            }
          },
          "subtitle": "У вас 99",
          "title": "Активность не ниже 70",
          "type": "tip_detail"
        },
        {
          "left_tip": {
            "background_color": "#F1F0ED",
            "form": "round",
            "icon": {
              "icon_type": "check",
              "tint_color": "#0596FA"
            }
          },
          "subtitle": "У вас: Любой",
          "title": "Способ оплаты Любой",
          "type": "tip_detail"
        },
        {
          "left_tip": {
            "background_color": "#F1F0ED",
            "form": "round",
            "icon": {
              "icon_type": "check",
              "tint_color": "#0596FA"
            }
          },
          "subtitle": "Вы в синей зоне ",
          "title": "Нахождение в синей зоне",
          "type": "tip_detail"
        },
        {
          "left_tip": {
            "background_color": "#F1F0ED",
            "form": "round",
            "icon": {
              "icon_type": "check",
              "tint_color": "#0596FA"
            }
          },
          "subtitle": "У вас Эконом, UberX, Специальный",
          "title": "Эконом, UberX, Специальный",
          "type": "tip_detail"
        }
      ],
      "geoareas": [
        {
          "id": "71b7eb1434ed42a99b101c40bdd2c8e7",
          "is_in_area": true
        }
      ],
      "id": "_id/5e4ac31d8fe28d5ce4be0dab",
      "toolbar_item": {
        "left_tip": {
          "background_color": "#0596FA",
          "form": "round",
          "icon": {
            "icon_type": "time",
            "tint_color": "#FFFFFF"
          },
          "size": "mu_6"
        },
        "primary_max_lines": 1,
        "primary_text_size": "title_small",
        "reverse": true,
        "secondary_text_color": "#0596FA",
        "subtitle": "4 ч 26 мин",
        "title": "Вы в синей зоне ",
        "type": "tip_detail"
      }
    },
    {
      "are_restrictions_satisfied": true,
      "description_items": [
        {
          "type": "title"
        },
        {
          "title": "Требования",
          "type": "title"
        },
        {
          "left_tip": {
            "background_color": "#F1F0ED",
            "form": "round",
            "icon": {
              "icon_type": "check",
              "tint_color": "#0596FA"
            }
          },
          "subtitle": "У вас Специальный",
          "title": "Специальный",
          "type": "tip_detail"
        }
      ],
      "id": "_id/5d551edcc081365f035eaed3"
    }
  ]
})JSON";

}  // namespace

TEST(JsonsComparison, TestComparator) {
  {
    const Json::Value lhs;
    ASSERT_EQ(ujc::GetJsonsDiff(lhs, lhs), boost::none);
  }
  {
    const Json::Value lhs{Json::ValueType::arrayValue};
    ASSERT_EQ(ujc::GetJsonsDiff(lhs, lhs), boost::none);
  }
  {
    const Json::Value lhs{Json::ValueType::objectValue};
    ASSERT_EQ(ujc::GetJsonsDiff(lhs, lhs), boost::none);
  }
  {
    const auto lhs = ReadJson(R"JSON({
      "obj": {
        "arr": [ "1", 2, 3.0, {}],
        "int": 1,
        "double": 1.2,
        "str": "s"
      }
    })JSON");

    ASSERT_EQ(ujc::GetJsonsDiff(lhs, lhs), boost::none);
  }
  {
    const auto lhs = ReadJson(R"JSON({
      "obj": {
        "int": 1,
        "double": 1.2
      }
    })JSON");
    const auto rhs = ReadJson(R"JSON({
      "obj": {
        "double": 1.2,
        "int": 1
      }
    })JSON");
    ASSERT_EQ(ujc::GetJsonsDiff(lhs, rhs), boost::none);
  }
  {
    const auto lhs = ReadJson(R"JSON({
      "arr": [1, 2]
    })JSON");
    const auto rhs = ReadJson(R"JSON({
      "arr": [2, 1]
    })JSON");
    const auto diff = ujc::GetJsonsDiff(lhs, rhs);
    ASSERT_TRUE(diff != boost::none);
    ASSERT_EQ(diff->lhs_diff, lhs);
    ASSERT_EQ(diff->rhs_diff, rhs);
  }
  {
    const auto lhs = ReadJson(R"JSON({
      "obj": {
        "arr": [ "1", 2, 3.0, {}],
        "int": 1,
        "double": 1.2,
        "str": "s"
      }
    })JSON");
    const auto rhs = ReadJson(R"JSON({
      "obj": {
        "arr": [ "1", 2, 3.0, {"arr":[]}],
        "int": 1,
        "double": 1.2,
        "str": "s"
      }
    })JSON");
    const auto diff = ujc::GetJsonsDiff(lhs, rhs);
    ASSERT_TRUE(diff != boost::none);
    ASSERT_EQ(diff->lhs_diff, ReadJson(R"JSON({
      "obj": {
        "arr": [{}]
      }
    })JSON"));
    ASSERT_EQ(diff->rhs_diff, ReadJson(R"JSON({
      "obj": {
        "arr": [{"arr":[]}]
      }
    })JSON"));
  }
  {
    const auto lhs = ReadJson(R"JSON({
      "obj": {
        "a": 1,
        "b": 2.0
      }
    })JSON");
    const auto rhs = ReadJson(R"JSON({
      "obj": {
        "a": 1.0,
        "b": 2
      }
    })JSON");
    const auto diff = ujc::GetJsonsDiff(lhs, rhs);
    ASSERT_TRUE(diff != boost::none);
    ASSERT_EQ(diff->lhs_diff, lhs);
    ASSERT_EQ(diff->rhs_diff, rhs);
  }
  {
    const auto lhs = ReadJson(R"JSON({
      "arr": [1, 2]
    })JSON");
    const auto rhs = ReadJson(R"JSON({
      "arr": [1]
    })JSON");
    const auto diff = ujc::GetJsonsDiff(lhs, rhs);
    ASSERT_TRUE(diff != boost::none);
    ASSERT_EQ(diff->lhs_diff, ReadJson(R"JSON({
      "arr": [2]
    })JSON"));
    ASSERT_EQ(diff->rhs_diff, ReadJson(R"JSON({
      "arr": []
    })JSON"));
  }
  {
    const auto lhs = ReadJson(kSubventionsStatusExample1);
    const auto rhs = ReadJson(kSubventionsStatusExample2);
    const auto diff = ujc::GetJsonsDiff(lhs, rhs);
    ASSERT_TRUE(diff != boost::none);
    ASSERT_EQ(diff->lhs_diff, ReadJson(R"JSON({
      "subventions_status": [
        {
          "description_items": [
            {
              "left_tip": {
                "icon": {
                  "tint_color": "#0596FA"
                }
              }
            }
          ]
        }
      ]
    })JSON"));
    ASSERT_EQ(diff->rhs_diff, ReadJson(R"JSON({
      "subventions_status": [
        {
          "description_items": [
            {
              "left_tip": {
                "icon": {
                  "tint_color": "#0596FB"
                }
              }
            }
          ]
        }
      ]
    })JSON"));
  }
}

TEST(JsonsComparison, TestNullOrEmpty) {
  {
    const auto lhs = ReadJson("{}");
    const auto rhs = ReadJson("{}");

    ASSERT_EQ(ujc::GetJsonsDiff(lhs, rhs), boost::none);
  }

  {
    const auto lhs = ReadJson("null");
    const auto rhs = ReadJson("{}");

    ASSERT_EQ(ujc::GetJsonsDiff(lhs, rhs), boost::none);
  }

  {
    const auto lhs = ReadJson("{\"property\": \"value\"}");
    const auto rhs = ReadJson("{}");

    const auto diff = ujc::GetJsonsDiff(lhs, rhs);
    ASSERT_TRUE(diff != boost::none);
    ASSERT_EQ(diff->lhs_diff, lhs);
    ASSERT_EQ(diff->rhs_diff, rhs);
  }
}
