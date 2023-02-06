#include "places_catalog_storage.hpp"

#include <gtest/gtest.h>

#include <geometry/position.hpp>
#include <userver/dump/test_helpers.hpp>

#include <models/catalog.hpp>

namespace caches {

namespace models = eats_restapp_marketing::models::catalog;
namespace storage = clients::eats_catalog_storage;

TEST(PlaceFromCatalogStorageCache, ReadWrite) {
  const models::Place place{
      1,                              // id
      models::DeliveryType::kNative,  // delivery_type
      geometry::Position{
          geometry::Longitude{12.0},
          geometry::Latitude{14.0},
      },  // point
      models::Brand{
          22,       // id
          "brand",  // slug
      },            // brand
  };

  const auto writen = dump::ToBinary<models::Place>(place);
  const auto read = dump::FromBinary<models::Place>(writen);

  EXPECT_EQ(place.id, read.id);
  EXPECT_EQ(place.point, read.point);
  EXPECT_EQ(place.brand.id, read.brand.id);
  EXPECT_EQ(place.brand.slug, read.brand.slug);
};

TEST(PlaceFromCatalogStorageCache, Convert) {
  storage::Brand brand;
  {
    brand.id = 2;
    brand.slug = "brand";
  }

  storage::PlacesItem item;
  {
    item.id = 1;
    item.sorting = {1};
    item.location = storage::Location{geometry::Position{
        geometry::Longitude{12.0}, geometry::Latitude{13.0}}};
    item.type = storage::PlaceType::kNative;
    item.business = storage::PlaceBusiness::kZapravki;
    item.categories = std::vector<storage::Category>{{12, "category"}};
    item.brand = brand;
  }

  const auto place = PlacesCacheTraits::Convert(storage::PlacesItem(item));

  ASSERT_TRUE(place.has_value());

  EXPECT_EQ(place->id, 1);
  EXPECT_EQ(place->point, item.location->geo_point);
  EXPECT_EQ(place->brand.id, 2);
  EXPECT_EQ(place->brand.slug, "brand");
}

TEST(PlaceFromCatalogStorageCache, ConvertInvalid) {
  storage::PlacesItem item;
  const auto place = PlacesCacheTraits::Convert(storage::PlacesItem(item));
  ASSERT_FALSE(place.has_value());
}

}  // namespace caches
