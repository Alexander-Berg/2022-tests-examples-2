#include <gtest/gtest.h>

#include <userver/dump/test_helpers.hpp>
#include "places_catalog_storage.hpp"

TEST(ReadWrite, PlaceFromCatalogStorageDump) {
  caches::PlaceFromCatalogStorage test_value = {
      13,
      std::optional(utils::geometry::Point(546.24, 235.234)),
      123,
      321,
      1,
      "UTC",
      clients::eats_catalog_storage::PlaceBusiness::kStore,
      clients::eats_catalog_storage::Category{0, "name"},
      eats_plus::models::Currency{"RUB"},
      clients::eats_catalog_storage::PlaceType::kNative};

  auto writed = dump::ToBinary<caches::PlaceFromCatalogStorage>(test_value);
  auto readed = dump::FromBinary<caches::PlaceFromCatalogStorage>(writed);

  EXPECT_EQ(test_value.place_id, readed.place_id);
  EXPECT_EQ(test_value.point, readed.point);
  EXPECT_EQ(test_value.region_id, readed.region_id);
  EXPECT_EQ(test_value.brand_id, readed.brand_id);
  EXPECT_EQ(test_value.country_id, readed.country_id);
  EXPECT_EQ(test_value.time_zone, readed.time_zone);
  EXPECT_EQ(test_value.business_type, readed.business_type);
  EXPECT_EQ(test_value.main_category, readed.main_category);
  EXPECT_EQ(test_value.currency, readed.currency);
  EXPECT_EQ(test_value.delivery_type, readed.delivery_type);
}

TEST(ReadWrite, PlaceFromCatalogStorageDumpNull) {
  caches::PlaceFromCatalogStorage test_value = {
      13,
      std::nullopt,
      333,
      321,
      1,
      "UTC",
      clients::eats_catalog_storage::PlaceBusiness::kRestaurant,
      std::nullopt,
      eats_plus::models::Currency{"RUB"},
      clients::eats_catalog_storage::PlaceType::kMarketplace};

  auto writed = dump::ToBinary<caches::PlaceFromCatalogStorage>(test_value);
  auto readed = dump::FromBinary<caches::PlaceFromCatalogStorage>(writed);

  EXPECT_EQ(test_value.place_id, readed.place_id);
  EXPECT_EQ(test_value.point, readed.point);
  EXPECT_EQ(test_value.region_id, readed.region_id);
  EXPECT_EQ(test_value.brand_id, readed.brand_id);
  EXPECT_EQ(test_value.country_id, readed.country_id);
  EXPECT_EQ(test_value.time_zone, readed.time_zone);
  EXPECT_EQ(test_value.business_type, readed.business_type);
  EXPECT_EQ(test_value.main_category, readed.main_category);
  EXPECT_EQ(test_value.currency, readed.currency);
  EXPECT_EQ(test_value.delivery_type, readed.delivery_type);
}

TEST(ReadWrite, PointDump) {
  utils::geometry::Point test_value(12.3215, 54.2345);
  dump::TestWriteReadCycle<utils::geometry::Point>(test_value);
}

TEST(ReadWrite, CategoryDump) {
  clients::eats_catalog_storage::Category test_value{12, "some_name"};
  dump::TestWriteReadCycle<clients::eats_catalog_storage::Category>(test_value);
}

TEST(Convert, PlacesCacheTraitsConvert) {
  using clients::eats_catalog_storage::Brand;
  using clients::eats_catalog_storage::Category;
  using clients::eats_catalog_storage::Country;
  using clients::eats_catalog_storage::Location;
  using clients::eats_catalog_storage::PlaceBusiness;
  using clients::eats_catalog_storage::PlacesItem;
  using clients::eats_catalog_storage::PlaceType;
  using clients::eats_catalog_storage::Region;

  Location geopoint;
  {
    geopoint.geo_point.SetLatitudeFromDouble(123.456);
    geopoint.geo_point.SetLongitudeFromDouble(654.321);
  }

  Region region;
  {
    region.id = 2222;
    region.geobase_ids = {1, 2, 3, 4, 5};
    region.time_zone = "Europe/Moscow";
  }

  Brand brand;
  {
    brand.id = 321;
    brand.slug = "slug";
    brand.name = "name";
  }

  Country country;
  {
    country.id = 1;
    country.code = "abc";
    country.name = "USSR";
    country.currency = {"$", "RUB"};
  }

  Category category;
  {
    country.id = 1;
    country.name = "name";
  }

  PlacesItem item;
  {
    item.id = 1998;
    item.location = std::optional<Location>(std::in_place, geopoint);
    item.region = std::optional<Region>(std::in_place, region);
    item.brand = std::optional<Brand>(std::in_place, brand);
    item.country = std::optional<Country>(std::in_place, country);
    item.categories = {category};
    item.business = PlaceBusiness::kShop;
    item.type = PlaceType::kMarketplace;
  }

  const auto result = caches::PlacesCacheTraits::Convert(PlacesItem{item});

  ASSERT_TRUE(result.has_value());

  EXPECT_EQ(result->place_id, item.id);
  EXPECT_EQ(result->point.value().lat,
            item.location->geo_point.GetLatitudeAsDouble());
  EXPECT_EQ(result->point.value().lon,
            item.location->geo_point.GetLongitudeAsDouble());
  EXPECT_EQ(result->region_id, item.region->id);
  EXPECT_EQ(result->brand_id, item.brand->id);
  EXPECT_EQ(result->country_id, item.country->id);
  EXPECT_EQ(result->time_zone, item.region->time_zone);
  EXPECT_EQ(*result->main_category, item.categories->front());
  EXPECT_EQ(result->business_type, *item.business);
  EXPECT_EQ(result->currency, "RUB");
  EXPECT_EQ(result->delivery_type, PlaceType::kMarketplace);
}

TEST(Convert, PlacesCacheTraitsConvertLocationNull) {
  using clients::eats_catalog_storage::Brand;
  using clients::eats_catalog_storage::Category;
  using clients::eats_catalog_storage::Country;
  using clients::eats_catalog_storage::PlaceBusiness;
  using clients::eats_catalog_storage::PlacesItem;
  using clients::eats_catalog_storage::PlaceType;
  using clients::eats_catalog_storage::Region;

  Region region;
  {
    region.id = 4321;
    region.geobase_ids = {6, 22, 333, 4445, 5567};
    region.time_zone = "Europe/Moscow";
  }

  Brand brand;
  {
    brand.id = 321;
    brand.slug = "slug";
    brand.name = "name";
  }

  Country country;
  {
    country.id = 1;
    country.code = "abc";
    country.name = "USSR";
    country.currency = {"$", "RUB"};
  }

  Category category;
  {
    country.id = 1;
    country.name = "name";
  }

  PlacesItem item;
  {
    item.id = 777;
    item.location = std::nullopt;
    item.region = std::optional<Region>(std::in_place, region);
    item.brand = std::optional<Brand>(std::in_place, brand);
    item.country = std::optional<Country>(std::in_place, country);
    item.categories = {category};
    item.business = PlaceBusiness::kPharmacy;
    item.type = PlaceType::kMarketplace;
  }

  const auto result_null = caches::PlacesCacheTraits::Convert(PlacesItem{item});

  ASSERT_TRUE(result_null.has_value());

  EXPECT_EQ(result_null->place_id, item.id);
  EXPECT_EQ(result_null->point, std::nullopt);
  EXPECT_EQ(result_null->region_id, item.region->id);
  EXPECT_EQ(result_null->time_zone, item.region->time_zone);
  EXPECT_EQ(result_null->brand_id, item.brand->id);
  EXPECT_EQ(result_null->country_id, item.country->id);
  EXPECT_EQ(*result_null->main_category, item.categories->front());
  EXPECT_EQ(result_null->business_type, *item.business);
  EXPECT_EQ(result_null->currency, "RUB");
  EXPECT_EQ(result_null->delivery_type, item.type);
}

TEST(Convert, PlacesCacheTraitsConvertInvalidItem) {
  using clients::eats_catalog_storage::PlacesItem;

  PlacesItem item;
  {
    item.id = 777;
    item.location = std::nullopt;
  }

  ASSERT_ANY_THROW(caches::PlacesCacheTraits::Convert(PlacesItem{item}));
}
