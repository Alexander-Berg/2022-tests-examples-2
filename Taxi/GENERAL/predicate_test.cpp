#include <unordered_set>
#include <variant>

#include <gtest/gtest.h>

#include <userver/formats/json.hpp>

#include <eats-catalog-predicate/builder.hpp>
#include <eats-catalog-predicate/collection/exceptions.hpp>
#include <eats-catalog-predicate/collection/predicate.hpp>

namespace eats_catalog_predicate::collection {

namespace {

using ::clients::catalog::libraries::eats_catalog_predicate::Argument;
using ::clients::catalog::libraries::eats_catalog_predicate::Predicate;
using ::clients::catalog::libraries::eats_catalog_predicate::PredicateInit;
using ::clients::catalog::libraries::eats_catalog_predicate::PredicateType;
using ::clients::catalog::libraries::eats_catalog_predicate::ValueType;

// T is string or int
template <class T>
std::unordered_set<std::variant<std::string, int>> SetToVariantSet(
    const std::unordered_set<T>& value) {
  return {value.begin(), value.end()};
}

}  // namespace

TEST(Collection, ParseError) {
  eats_catalog_predicate::collection::Parser parser{};

  constexpr std::string_view kCollectionJson = R"(
  {
    "slug": "test",
    "title": "MyTitle",
    "description": "MyDescription",
    "searchConditions": {
      "strategy": "unknow_strategy",
      "arguments": {
        "brand_ids": [
          737
        ]
      }
    }
  }
  )";

  const auto json = formats::json::FromString(kCollectionJson);
  ASSERT_THROW(parser.Parse(json), collection::InvalidCollectionFromat);
}

TEST(Collection, Parse) {
  eats_catalog_predicate::collection::Parser parser{};

  constexpr std::string_view kCollectionJson = R"(
  {
    "slug": "test",
    "title": "MyTitle",
    "actions": {
      "addMetaToPlace": [
        {
          "meta": {
            "description": "Description",
            "informationBlocks": []
          },
          "brand_slug": "my_brand_slug"
        },
        {
          "meta": {
            "isAds": true,
            "description": "Description Place",
            "informationBlocks": []
          },
          "place_id": 1
        }
      ]
    },
    "description": "MyDescription",
    "searchConditions": {
      "strategy": "by_brand_id",
      "arguments": {
        "brand_ids": [
          737
        ]
      }
    }
  }
  )";

  const auto json = formats::json::FromString(kCollectionJson);
  const auto info = parser.Parse(json);

  {
    const std::unordered_set<int> brand_ids{737};

    const auto expected =
        PredicateBuilder()
            .All({
                PredicateBuilder()
                    .Any({
                        PredicateBuilder()
                            .ShippingTypes()
                            .Contains("pickup")
                            .Build(),
                        PredicateBuilder()
                            .ShippingTypes()
                            .Contains("delivery")
                            .Build(),
                    })
                    .Build(),
                PredicateBuilder().BrandId().InSet(brand_ids).Build(),
            })
            .Build();
    EXPECT_EQ(info.shipping_type, eats_shared::ShippingType::kDelivery);
    ASSERT_EQ(info.predicate, expected);
  }
}

TEST(Collection, ParseShipping) {
  eats_catalog_predicate::collection::Parser parser{};

  constexpr std::string_view kCollectionJson = R"(
  {
    "slug": "test",
    "title": "MyTitle",
    "actions": {
      "addMetaToPlace": [
        {
          "meta": {
            "description": "Description",
            "informationBlocks": []
          },
          "brand_slug": "my_brand_slug"
        },
        {
          "meta": {
            "isAds": true,
            "description": "Description Place",
            "informationBlocks": []
          },
          "place_id": 1
        }
      ]
    },
    "description": "MyDescription",
    "searchConditions": {
      "strategy": "by_place_id",
      "shipping_type": "pickup",
      "arguments": {
        "place_ids": [ 1, 2, 3 ]
      }
    }
  }
  )";

  const auto json = formats::json::FromString(kCollectionJson);
  const auto info = parser.Parse(json);

  {
    const std::unordered_set<int> place_ids{1, 2, 3};
    const auto expected =
        PredicateBuilder()
            .All({
                PredicateBuilder().ShippingTypes().Contains("pickup").Build(),
                PredicateBuilder().PlaceId().InSet(place_ids).Build(),
            })
            .Build();
    EXPECT_EQ(info.shipping_type, eats_shared::ShippingType::kPickup);
    ASSERT_EQ(info.predicate, expected);
  }
}

}  // namespace eats_catalog_predicate::collection
