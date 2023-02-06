#include "collections.hpp"

#include <gtest/gtest.h>

#include <fmt/format.h>

namespace {

using eats_layout_constructor::models::CollectionPlacesDataMap;
using eats_layout_constructor::sources::PlaceId;
using eats_layout_constructor::sources::catalog::Place;
using eats_layout_constructor::utils::collections::CollectionPlacesEditor;

std::vector<Place> MakePlaces(size_t count, bool add_meta = false) {
  std::vector<Place> result;
  for (size_t i = 0; i < count; i++) {
    formats::json::ValueBuilder builder{formats::common::Type::kObject};
    builder["brand"] = formats::common::Type::kObject;
    builder["brand"]["slug"] = fmt::format("slug_{}", i);
    if (add_meta) {
      formats::json::ValueBuilder layout{formats::common::Type::kObject};
      layout["type"] = "meta";
      layout["layout"] = formats::common::Type::kArray;
      builder["layout"].PushBack(std::move(layout));

      builder["data"]["meta"] = formats::common::Type::kArray;
    }
    auto& place = result.emplace_back();
    place.meta.place_id = PlaceId(i);
    place.payload = builder.ExtractValue();
  }
  return result;
}

}  // namespace

TEST(CollectionPlacesEditor, EditPlacesByBrandSlug) {
  constexpr std::string_view kCollectionJson = R"(
  {
    "actions": {
      "addMetaToPlace": [
        {
          "meta": {
            "description": "Description",
            "informationBlocks": []
          },
          "brand_slug": "slug_0"
        }
      ]
    }
  }
  )";
  auto value = formats::json::FromString(kCollectionJson);
  CollectionPlacesDataMap data_map("test", value);
  CollectionPlacesEditor editor("test", data_map, {});
  auto places = MakePlaces(1);
  editor.EditPlaces(places);
  auto result_description =
      places.front().payload["data"]["features"]["review"]["description"];
  ASSERT_EQ(result_description.As<std::string>(), "Description");
}

TEST(CollectionPlacesEditor, EditPlacesByPlaceId) {
  constexpr std::string_view kCollectionJson = R"(
  {
    "actions": {
      "addMetaToPlace": [
        {
          "meta": {
            "description": "Description",
            "informationBlocks": []
          },
          "place_id": 0
        }
      ]
    }
  }
  )";
  auto value = formats::json::FromString(kCollectionJson);
  CollectionPlacesDataMap data_map("test", value);
  CollectionPlacesEditor editor("test", data_map, {});
  auto places = MakePlaces(2);
  editor.EditPlaces(places);
  auto result_description =
      places.front().payload["data"]["features"]["review"]["description"];
  ASSERT_EQ(result_description.As<std::string>(), "Description");

  // ресторан без ревью остался в подборке
  ASSERT_EQ(places.size(), 2);
}

TEST(CollectionPlacesEditor, Rank) {
  constexpr std::string_view kCollectionJson = R"(
  {
    "actions": {
      "addMetaToPlace": [
        {
          "meta": {
            "description": "Description",
            "informationBlocks": []
          },
          "place_id": 0
        },
        {
          "meta": {
            "description": "Description",
            "informationBlocks": []
          },
          "position": 1,
          "place_id": 1
        }
      ]
    }
  }
  )";
  auto value = formats::json::FromString(kCollectionJson);
  CollectionPlacesDataMap data_map("test", value);
  CollectionPlacesEditor editor("test", data_map, {});
  auto places = MakePlaces(2);
  editor.RankPlaces(places);
  ASSERT_EQ(places.front().meta.place_id.GetUnderlying(), 1);
  ASSERT_EQ(places.back().meta.place_id.GetUnderlying(), 0);
}

TEST(CollectionPlacesEditor, RankLargePosition) {
  constexpr std::string_view kCollectionJson = R"(
  {
    "actions": {
      "addMetaToPlace": [
        {
          "meta": {
            "description": "Description",
            "informationBlocks": []
          },
          "position": 100,
          "place_id": 0
        },
        {
          "meta": {
            "description": "Description",
            "informationBlocks": []
          },
          "place_id": 1
        }
      ]
    }
  }
  )";
  auto value = formats::json::FromString(kCollectionJson);
  CollectionPlacesDataMap data_map("test", value);
  CollectionPlacesEditor editor("test", data_map, {});
  auto places = MakePlaces(2);
  editor.RankPlaces(places);
  ASSERT_EQ(places.front().meta.place_id.GetUnderlying(), 1);
  ASSERT_EQ(places.back().meta.place_id.GetUnderlying(), 0);
}

TEST(CollectionPlacesEditor, RankSpecialCase) {
  constexpr std::string_view kCollectionJson = R"(
  {
    "actions": {
      "addMetaToPlace": [
        {
          "meta": {
            "description": "Description",
            "informationBlocks": []
          },
          "place_id": 0
        },
        {
          "meta": {
            "description": "Description",
            "informationBlocks": []
          },
          "position": 1,
          "place_id": 1
        },
        {
          "meta": {
            "description": "Description",
            "informationBlocks": []
          },
          "position": 2,
          "place_id": 2
        }
      ]
    }
  }
  )";
  auto value = formats::json::FromString(kCollectionJson);
  CollectionPlacesDataMap data_map("test", value);
  CollectionPlacesEditor editor("test", data_map, {});
  auto places = MakePlaces(3);
  editor.RankPlaces(places);
  ASSERT_EQ(places[0].meta.place_id.GetUnderlying(), 1);
  ASSERT_EQ(places[1].meta.place_id.GetUnderlying(), 2);
  ASSERT_EQ(places[2].meta.place_id.GetUnderlying(), 0);
}

TEST(CollectionPlacesEditor, RankMix) {
  constexpr std::string_view kCollectionJson = R"(
  {
    "actions": {
      "addMetaToPlace": [
        {
          "meta": {
            "description": "Description",
            "informationBlocks": []
          },
          "position": 100,
          "place_id": 0
        },
        {
          "meta": {
            "description": "Description",
            "informationBlocks": []
          },
          "position": 1,
          "place_id": 1
        },
        {
          "meta": {
            "description": "Description",
            "informationBlocks": []
          },
          "place_id": 2
        }
      ]
    }
  }
  )";
  auto value = formats::json::FromString(kCollectionJson);
  CollectionPlacesDataMap data_map("test", value);
  CollectionPlacesEditor editor("test", data_map, {});
  auto places = MakePlaces(3);
  editor.RankPlaces(places);
  ASSERT_EQ(places[0].meta.place_id.GetUnderlying(), 1);
  ASSERT_EQ(places[1].meta.place_id.GetUnderlying(), 2);
  ASSERT_EQ(places[2].meta.place_id.GetUnderlying(), 0);
}

TEST(CollectionPlacesEditor, EditAds) {
  constexpr std::string_view kCollectionJson = R"(
  {
    "actions": {
      "addMetaToPlace": [
        {
          "meta": {
            "isAds": true,
            "description": "Description",
            "informationBlocks": []
          },
          "brand_slug": "slug_0"
        }
      ]
    }
  }
  )";
  constexpr std::string_view kColorConfigJson = R"(
  {
    "text": {
      "text": "реклама",
      "color": [
        {
          "theme": "light",
          "value": "#000000"
        },
        {
          "theme": "dark",
          "value": "#FFFFFF"
        }
      ]
    },
    "background": [
      {
        "theme": "light",
        "value": "#FAE3AA"
      },
      {
        "theme": "dark",
        "value": "#674718"
      }
    ]
  }
  )";
  auto value = formats::json::FromString(kCollectionJson);
  auto ads_text = formats::json::FromString(kColorConfigJson);
  CollectionPlacesDataMap data_map("test", value);
  CollectionPlacesEditor editor("test", data_map, ads_text);
  auto places = MakePlaces(1);
  editor.EditPlaces(places);

  ASSERT_EQ(places.front().payload["layout"].GetSize(), 1);
  ASSERT_EQ(places.front().payload["layout"][0]["type"].As<std::string>(),
            "meta");
  ASSERT_EQ(places.front()
                .payload["layout"][0]["layout"][0]["type"]
                .As<std::string>(),
            "advertisements");

  auto meta = places.front().payload["data"]["meta"];

  ASSERT_EQ(meta.GetSize(), 1);

  auto meta_payload = meta[0]["payload"];
  ASSERT_EQ(meta_payload["text"]["text"].As<std::string>(), "реклама");

  ASSERT_TRUE(meta_payload["text"]["color"].IsArray());
  ASSERT_EQ(meta_payload["text"]["color"].GetSize(), 2);

  ASSERT_TRUE(meta_payload["background"].IsArray());
  ASSERT_EQ(meta_payload["background"].GetSize(), 2);
}

TEST(CollectionPlacesEditor, EditAdsAlreadyHasMeta) {
  constexpr std::string_view kCollectionJson = R"(
  {
    "actions": {
      "addMetaToPlace": [
        {
          "meta": {
            "isAds": true,
            "description": "Description",
            "informationBlocks": []
          },
          "brand_slug": "slug_0"
        }
      ]
    }
  }
  )";
  constexpr std::string_view kColorConfigJson = R"(
  {
    "text": "реклама"
  }
  )";
  auto value = formats::json::FromString(kCollectionJson);
  auto ads_text = formats::json::FromString(kColorConfigJson);
  CollectionPlacesDataMap data_map("test", value);
  CollectionPlacesEditor editor("test", data_map, ads_text);
  auto places = MakePlaces(1, true);
  editor.EditPlaces(places);

  ASSERT_EQ(places.front().payload["layout"].GetSize(), 1);
  ASSERT_EQ(places.front().payload["layout"][0]["type"].As<std::string>(),
            "meta");
  ASSERT_EQ(places.front()
                .payload["layout"][0]["layout"][0]["type"]
                .As<std::string>(),
            "advertisements");

  auto meta = places.front().payload["data"]["meta"];

  ASSERT_EQ(meta.GetSize(), 1);

  auto meta_payload = meta[0]["payload"];
  ASSERT_EQ(meta_payload["text"].As<std::string>(), "реклама");
}
