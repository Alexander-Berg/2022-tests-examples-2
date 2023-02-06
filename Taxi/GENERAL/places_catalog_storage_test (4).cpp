#include "places_catalog_storage.hpp"

#include <gtest/gtest.h>

#include <geometry/position.hpp>
#include <userver/dump/test_helpers.hpp>

#include <models/catalog.hpp>

namespace caches {

namespace models = umlaas_eats::models::catalog;
namespace storage = clients::eats_catalog_storage;

TEST(PlaceFromCatalogStorageCache, ReadWrite) {
  const models::Place place{
      models::PlaceId(1),             // id
      models::PlaceSlug{"slug0"},     // slug
      1,                              // weight
      models::DeliveryType::kNative,  // delivery_type
      geometry::Position{
          geometry::Longitude{12.0},
          geometry::Latitude{14.0},
      },  // point
      models::Brand{
          models::BrandId(22),          // id
          "brand",                      // slug
          models::Business::kPharmacy,  // business
      },                                // brand
      models::PriceCategory{
          131,  // id
          213,  // value
      },        // price_category
      models::Rating{
          100.0,         // value
          121.0,         // average
          std::nullopt,  // shown
          13232,         // count
      },                 // rating
      models::NewRating{
          231.121,  // value
          false,    // show
      },            // new_rating
      models::Place::Times{
          10,   // extra_preparation_minutes
          20,   // avg_preparation_minutes
      },        // times
      true,     // is_fast_food
      {"tag"},  // tags
  };

  const auto writen = dump::ToBinary<models::Place>(place);
  const auto read = dump::FromBinary<models::Place>(writen);

  EXPECT_EQ(place.id, read.id);
  EXPECT_EQ(place.weight, read.weight);
  EXPECT_EQ(place.point, read.point);
  EXPECT_EQ(place.brand.id, read.brand.id);
  EXPECT_EQ(place.brand.slug, read.brand.slug);
  EXPECT_EQ(place.brand.business, read.brand.business);
  EXPECT_EQ(place.price_category.id, read.price_category.id);
  EXPECT_EQ(place.price_category.value, read.price_category.value);
  EXPECT_EQ(place.rating.value, read.rating.value);
  EXPECT_EQ(place.rating.average, read.rating.average);
  EXPECT_EQ(place.rating.shown, read.rating.shown);
  EXPECT_EQ(place.rating.count, read.rating.count);
  EXPECT_EQ(place.times.extra_preparation_minutes,
            read.times.extra_preparation_minutes);
  EXPECT_EQ(place.times.avg_preparation_minutes,
            read.times.avg_preparation_minutes);

  ASSERT_TRUE(place.new_rating.has_value() && read.new_rating.has_value());
  EXPECT_EQ(place.new_rating->value, read.new_rating->value);
  EXPECT_EQ(place.new_rating->show, read.new_rating->show);
  EXPECT_EQ(place.is_fast_food, read.is_fast_food);
  EXPECT_EQ(place.slug, read.slug);
  EXPECT_EQ(place.tags, read.tags);
};

TEST(PlaceFromCatalogStorageCache, Convert) {
  storage::Sorting sorting;
  sorting.weight = 1;

  storage::Brand brand;
  {
    brand.id = 2;
    brand.slug = "brand";
  }

  storage::PriceCategory price_category;
  {
    price_category.id = 12;
    price_category.value = 131;
  }

  storage::Rating rating;
  {
    rating.admin = 12;
    rating.users = 14;
    rating.shown = std::nullopt;
    rating.count = 1234;
  }

  storage::NewRating new_rating;
  {
    new_rating.rating = 10.0;
    new_rating.show = true;
  }

  storage::Timing timing{};
  {
    timing.average_preparation = 600;
    timing.extra_preparation = 300;
  }

  storage::Feature featrue{};
  featrue.fast_food = true;

  storage::PlacesItem item;
  {
    item.id = 1;
    item.sorting = sorting;
    item.location = storage::Location{geometry::Position{
        geometry::Longitude{12.0}, geometry::Latitude{13.0}}};
    item.type = storage::PlaceType::kNative;
    item.business = storage::PlaceBusiness::kZapravki;
    item.categories = std::vector<storage::Category>{{12, "category"}};
    item.brand = brand;
    item.price_category = price_category;
    item.rating = rating;
    item.new_rating = new_rating;
    item.timing = timing;
    item.features = featrue;
    item.slug = "slug0";
  }

  const auto place = PlacesCacheTraits::Convert(storage::PlacesItem(item));

  ASSERT_TRUE(place.has_value());

  EXPECT_EQ(place->id, models::PlaceId(1));
  EXPECT_EQ(place->weight, 1);
  EXPECT_EQ(place->point, item.location->geo_point);
  EXPECT_EQ(place->brand.id, models::BrandId(2));
  EXPECT_EQ(place->brand.slug, "brand");
  EXPECT_EQ(place->brand.business, models::Business::kZapravki);
  EXPECT_EQ(place->price_category.id, 12);
  EXPECT_EQ(place->price_category.value, 131);
  EXPECT_EQ(place->rating.value, 12);
  EXPECT_EQ(place->rating.average, 14);
  EXPECT_EQ(place->rating.shown, std::nullopt);
  EXPECT_EQ(place->rating.count, 1234);
  EXPECT_EQ(place->times.extra_preparation_minutes, 5);
  EXPECT_EQ(place->times.avg_preparation_minutes, 10);
  EXPECT_EQ(place->is_fast_food, true);

  ASSERT_TRUE(place->new_rating.has_value());
  EXPECT_EQ(place->new_rating->value, 10);
  EXPECT_EQ(place->new_rating->show, true);
}

TEST(PlaceFromCatalogStorageCache, ConvertInvalid) {
  storage::PlacesItem item;
  const auto place = PlacesCacheTraits::Convert(storage::PlacesItem(item));
  ASSERT_FALSE(place.has_value());
}

}  // namespace caches
