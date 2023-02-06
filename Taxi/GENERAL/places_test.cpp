#include <gtest/gtest.h>

#include "places.hpp"

using eats_layout_constructor::utils::transformers::places::ToMiniPlace;

TEST(ToMiniPlace, Simple) {
  auto place = formats::json::FromString(R"(
    {
      "name": "Имя ресторана",
      "slug": "my_rest_slug",
      "brand": {
        "name": "Имя бренда",
        "slug": "my_brand_slug",
        "business": "restaurant"
      },
      "availability": {
        "is_available": true
      },
      "media": {
        "photos": [
          {
            "uri": "/images/1000/iddqd-{w}x{h}.jpg"
          }
        ]
      },
      "layout": [],
      "data": {
        "features": {}
      },
      "context": "hello",
      "analytics": "hello"
    }
  )");

  auto mini = ToMiniPlace(place).ExtractValue();

  EXPECT_FALSE(mini.IsNull());

  auto expected = formats::json::FromString(R"(
    {
      "name": "Имя ресторана",
      "slug": "my_rest_slug",
      "brand": {
        "name": "Имя бренда",
        "slug": "my_brand_slug",
        "business": "restaurant"
      },
      "availability": {
        "is_available": true
      },
      "media": {
        "photos": [
          {
            "uri": "/images/1000/iddqd-{w}x{h}.jpg"
          }
        ]
      },
      "data": {
        "features": {}
      },
      "context": "hello",
      "analytics": "hello"
    }
  )");

  ASSERT_EQ(expected, mini)
      << "Expected: " << formats::json::ToString(expected) << std::endl
      << "Actual: " << formats::json::ToString(mini);
}

TEST(ToMiniPlace, FullPlaceWithMetaAndActions) {
  auto place = formats::json::FromString(R"(
    {
      "name": "Имя ресторана",
      "slug": "my_rest_slug",
      "brand": {
        "name": "Имя бренда",
        "slug": "my_brand_slug",
        "business": "restaurant"
      },
      "availability": {
        "is_available": true
      },
      "media": {
        "photos": [
          {
            "uri": "/images/1000/iddqd-{w}x{h}.jpg"
          }
        ]
      },
      "layout": [
        {
          "type": "meta",
          "layout": [
            {
              "id": "fake_c48a1c13",
              "type": "rating"
            },
            {
              "id": "fake_333ec296",
              "type": "price_category"
            }
          ]
        },
        {
          "type": "actions",
          "layout": []
        }
      ],
      "data": {
        "features": {
          "delivery": {
            "text": "~45 мин"
          },
          "favorite": {
            "active": true
          }
        },
        "meta": [
          {
            "id": "fake_rating_id",
            "type": "rating",
            "payload": {
              "icon_url": "asset://flame",
              "color": [
                {
                  "theme": "dark",
                  "value": "#C4C2BE"
                },
                {
                  "theme": "light",
                  "value": "#C4C2BE"
                }
              ],
              "title": "4.7 Входит в Топ"
            }
          },
          {
            "id": "fake_price_category_id",
            "type": "price_category",
            "payload": {
              "icon_url": "asset://price_category",
              "currency_sign": "₽",
              "total_symbols": 3,
              "highlighted_symbols": 3
            }
          }
        ],
        "actions": [
          {
            "id": "fake_promo_id",
            "type": "promo",
            "payload": {
              "name": "50% на всё"
            }
          }
        ]
      },
      "context": "context_string",
      "analytics": "analytics_string",
      "link": {
          "deeplink": "http://test.orgnet"
      }
    }
  )");

  auto mini = ToMiniPlace(place).ExtractValue();

  EXPECT_FALSE(mini.IsNull());

  auto expected = formats::json::FromString(R"(
    {
      "name": "Имя ресторана",
      "slug": "my_rest_slug",
      "brand": {
        "name": "Имя бренда",
        "slug": "my_brand_slug",
        "business": "restaurant"
      },
      "availability": {
        "is_available": true
      },
      "media": {
        "photos": [
          {
            "uri": "/images/1000/iddqd-{w}x{h}.jpg"
          }
        ]
      },
      "data": {
        "features": {
          "delivery": {
            "text": "~45 мин"
          }
        }
      },
      "context": "context_string",
      "analytics": "analytics_string",
      "link": {
          "deeplink": "http://test.orgnet"
      }
    }
  )");

  ASSERT_EQ(expected, mini)
      << "Expected: " << formats::json::ToString(expected) << std::endl
      << "Actual: " << formats::json::ToString(mini);
}

TEST(ToMiniPlace, YandexPlus) {
  auto place = formats::json::FromString(R"(
    {
      "name": "Имя ресторана",
      "slug": "my_rest_slug",
      "availability": {
        "is_available": true
      },
      "layout": [
        {
          "type": "meta",
          "layout": [
            {
              "id": "fake_c48a1c13",
              "type": "yandex_plus"
            }
          ]
        }
      ],
      "data": {
        "features": {},
        "meta": [
          {
            "id": "fake_rating_id",
            "type": "yandex_plus",
            "payload": {
              "some": "random",
              "json": "here"
            }
          }
        ]
      },
      "context": "hello",
      "analytics": "hello"
    }
  )");

  auto mini = ToMiniPlace(place).ExtractValue();

  EXPECT_FALSE(mini.IsNull());

  auto expected = formats::json::FromString(R"(
    {
      "name": "Имя ресторана",
      "slug": "my_rest_slug",
      "availability": {
        "is_available": true
      },
      "data": {
        "features": {
          "yandex_plus": {
            "some": "random",
            "json": "here"
          }
        }
      },
      "context": "hello",
      "analytics": "hello"
    }
  )");

  ASSERT_EQ(expected, mini)
      << "Expected: " << formats::json::ToString(expected) << std::endl
      << "Actual: " << formats::json::ToString(mini);
}

TEST(ToMiniPlace, YandexPlusNoFeatrures) {
  auto place = formats::json::FromString(R"(
    {
      "name": "Имя ресторана",
      "slug": "my_rest_slug",
      "availability": {
        "is_available": true
      },
      "layout": [
        {
          "type": "meta",
          "layout": [
            {
              "id": "fake_c48a1c13",
              "type": "yandex_plus"
            }
          ]
        }
      ],
      "data": {
        "meta": [
          {
            "id": "fake_rating_id",
            "type": "yandex_plus",
            "payload": {
              "some": "random",
              "json": "here"
            }
          }
        ]
      },
      "context": "hello",
      "analytics": "hello"
    }
  )");

  auto mini = ToMiniPlace(place).ExtractValue();

  EXPECT_FALSE(mini.IsNull());

  auto expected = formats::json::FromString(R"(
    {
      "name": "Имя ресторана",
      "slug": "my_rest_slug",
      "availability": {
        "is_available": true
      },
      "data": {
        "features": {
          "yandex_plus": {
            "some": "random",
            "json": "here"
          }
        }
      },
      "context": "hello",
      "analytics": "hello"
    }
  )");

  ASSERT_EQ(expected, mini)
      << "Expected: " << formats::json::ToString(expected) << std::endl
      << "Actual: " << formats::json::ToString(mini);
}

TEST(ToMiniPlace, PartialData) {
  auto place = formats::json::FromString(R"(
    {
      "name": "Имя ресторана",
      "brand": {
        "name": "Имя бренда",
        "slug": "my_brand_slug",
        "business": "restaurant"
      },
      "availability": {
        "is_available": true
      },
      "data": {
        "features": {
          "favorite": {
            "active": true
          }
        }
      },
      "context": "hello",
      "analytics": "hello"
    }
  )");

  auto mini = ToMiniPlace(place).ExtractValue();

  EXPECT_FALSE(mini.IsNull());

  auto expected = formats::json::FromString(R"(
    {
      "name": "Имя ресторана",
      "brand": {
        "name": "Имя бренда",
        "slug": "my_brand_slug",
        "business": "restaurant"
      },
      "availability": {
        "is_available": true
      },
      "data": {
        "features": {}
      },
      "context": "hello",
      "analytics": "hello"
    }
  )");

  ASSERT_EQ(expected, mini)
      << "Expected: " << formats::json::ToString(expected) << std::endl
      << "Actual: " << formats::json::ToString(mini);
}

TEST(ToMiniPlace, EmptyObjectData) {
  auto place = formats::json::FromString(R"(
    {}
  )");

  auto mini = ToMiniPlace(place).ExtractValue();

  EXPECT_FALSE(mini.IsNull());

  auto expected = formats::json::FromString(R"(
    {}
  )");

  ASSERT_EQ(expected, mini)
      << "Expected: " << formats::json::ToString(expected) << std::endl
      << "Actual: " << formats::json::ToString(mini);
}

TEST(ToMiniPlace, NoData) {
  auto mini = ToMiniPlace({}).ExtractValue();

  EXPECT_TRUE(mini.IsNull());
}

TEST(ToMiniPlace, NonObjectData) {
  auto data = formats::json::ValueBuilder{"hello"}.ExtractValue();
  auto mini = ToMiniPlace(data).ExtractValue();

  EXPECT_TRUE(mini.IsNull());
}
