#include "collections.hpp"

#include <set>

#include <gtest/gtest.h>

#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value_builder.hpp>

#include <eats-catalog-predicate/collection/exceptions.hpp>

#include <exceptions/view_exception.hpp>

namespace {

using eats_layout_constructor::models::CollectionInfo;
using eats_layout_constructor::models::CollectionParseError;
using eats_layout_constructor::models::CollectionSearchInfo;

using eats_layout_constructor::sources::PlaceId;

using eats_layout_constructor::exceptions::ViewException;

}  // namespace

TEST(CollectionSearchInfo, UnknownSearchStrategy) {
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
  auto json = formats::json::FromString(kCollectionJson);
  ASSERT_THROW(parser.Parse(json),
               eats_catalog_predicate::collection::InvalidCollectionFromat);
}

TEST(CollectionInfo, Parse) {
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
  auto collection_info =
      CollectionInfo::Parse("slug", eats_catalog_predicate::collection::Info{},
                            formats::json::FromString(kCollectionJson));
  ASSERT_EQ(collection_info.GetSlug(), "slug");
  ASSERT_EQ(collection_info.GetTitle(), "MyTitle");
  ASSERT_EQ(collection_info.GetDescription(), "MyDescription");

  const auto& place_data_map = collection_info.GetPlacesDataMap();
  // search by brand slug
  {
    auto brand_slug =
        formats::json::ValueBuilder("my_brand_slug").ExtractValue();
    const auto* place_data =
        place_data_map.FindByBrandSlugOrPlaceId(brand_slug, PlaceId(100));
    ASSERT_NE(place_data, nullptr);
    ASSERT_EQ(place_data->review["description"].As<std::string>(),
              "Description");
  }

  // search by place_id
  {
    auto brand_slug = formats::json::ValueBuilder("smth").ExtractValue();
    const auto* place_data =
        place_data_map.FindByBrandSlugOrPlaceId(brand_slug, PlaceId(1));
    ASSERT_NE(place_data, nullptr);
    ASSERT_TRUE(place_data->is_ads);
    ASSERT_EQ(place_data->review["description"].As<std::string>(),
              "Description Place");
  }
}
