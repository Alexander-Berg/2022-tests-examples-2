#include <gtest/gtest.h>

#include <userver/dump/test_helpers.hpp>
#include "places_catalog_storage.hpp"

TEST(ReadWrite, RegionDump) {
  caches::Region test_value{111, {1, 2, 3}, "UTC", "region"};

  auto writed = dump::ToBinary<caches::Region>(test_value);
  auto readed = dump::FromBinary<caches::Region>(writed);

  EXPECT_EQ(test_value.id, readed.id);
  EXPECT_EQ(test_value.geobase_ids, readed.geobase_ids);
  EXPECT_EQ(test_value.name, readed.name);
  EXPECT_EQ(test_value.time_zone, readed.time_zone);
}

TEST(ReadWrite, RatingDump) {
  caches::Rating test_value{5.0, false};

  auto writed = dump::ToBinary<caches::Rating>(test_value);
  auto readed = dump::FromBinary<caches::Rating>(writed);

  EXPECT_EQ(test_value.rating, readed.rating);
  EXPECT_EQ(test_value.show, readed.show);
}

TEST(ReadWrite, PointDump) {
  utils::geometry::Point test_value{12.3215, 54.2345};
  dump::TestWriteReadCycle<utils::geometry::Point>(test_value);
}

TEST(ReadWrite, PlaceType) {
  using clients::eats_catalog_storage::PlaceType;
  PlaceType type = PlaceType::kNative;
  dump::TestWriteReadCycle<PlaceType>(type);
}

TEST(ReadWrite, Currency) {
  caches::Currency test_value{"RUB", "₽"};

  auto writed = dump::ToBinary<caches::Currency>(test_value);
  auto readed = dump::FromBinary<caches::Currency>(writed);

  EXPECT_EQ(test_value.code, readed.code);
  EXPECT_EQ(test_value.sign, readed.sign);
}

TEST(ReadWrite, Country) {
  caches::Country test_value{13, "RU", "Россия",
                             caches::Currency{"RUB", "₽"}};

  auto writed = dump::ToBinary<caches::Country>(test_value);
  auto readed = dump::FromBinary<caches::Country>(writed);

  EXPECT_EQ(test_value.id, readed.id);
  EXPECT_EQ(test_value.code, readed.code);
  EXPECT_EQ(test_value.name, readed.name);
  EXPECT_EQ(test_value.currency.code, readed.currency.code);
  EXPECT_EQ(test_value.currency.sign, readed.currency.sign);
}

TEST(ReadWrite, RestaurantType) {
  using clients::eats_catalog_storage::PlaceBusiness;
  PlaceBusiness type = PlaceBusiness::kRestaurant;
  dump::TestWriteReadCycle<PlaceBusiness>(type);
}

TEST(ReadWrite, PlaceFromCatalogStorageDump) {
  caches::PlaceFromCatalogStorage test_value = {
      utils::geometry::Point(546.24, 235.234),
      caches::Region{111, {1, 2, 3}, "UTC", "region"},
      caches::Rating{4.5, true},
      clients::eats_catalog_storage::PlaceType::kNative,
      caches::Country{13, "RU", "Россия", caches::Currency{"RUB", "₽"}},
      clients::eats_catalog_storage::PlaceBusiness::kRestaurant};

  auto writed = dump::ToBinary<caches::PlaceFromCatalogStorage>(test_value);
  auto readed = dump::FromBinary<caches::PlaceFromCatalogStorage>(writed);

  EXPECT_EQ(test_value.point, readed.point);

  EXPECT_EQ(test_value.region.id, readed.region.id);
  EXPECT_EQ(test_value.region.geobase_ids, readed.region.geobase_ids);
  EXPECT_EQ(test_value.region.name, readed.region.name);
  EXPECT_EQ(test_value.region.time_zone, readed.region.time_zone);

  EXPECT_EQ(test_value.rating->rating, readed.rating->rating);
  EXPECT_EQ(test_value.rating->show, readed.rating->show);

  EXPECT_EQ(test_value.type.value(), readed.type.value());

  EXPECT_EQ(test_value.country->id, readed.country->id);
  EXPECT_EQ(test_value.country->code, readed.country->code);
  EXPECT_EQ(test_value.country->name, readed.country->name);
  EXPECT_EQ(test_value.country->currency.code, readed.country->currency.code);
  EXPECT_EQ(test_value.country->currency.sign, readed.country->currency.sign);

  EXPECT_EQ(test_value.business_type.value(), readed.business_type.value());
}

TEST(ReadWrite, PlaceFromCatalogStorageDumpNull) {
  std::optional<caches::PlaceFromCatalogStorage> test_value{};

  auto writed = dump::ToBinary<std::optional<caches::PlaceFromCatalogStorage>>(
      test_value);
  auto readed =
      dump::FromBinary<std::optional<caches::PlaceFromCatalogStorage>>(writed);

  EXPECT_EQ(std::nullopt, readed);
}

TEST(Convert, PlacesCacheTraitsConvert) {
  using clients::eats_catalog_storage::Country;
  using clients::eats_catalog_storage::Location;
  using clients::eats_catalog_storage::NewRating;
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
    region.name = "REGION";
  }

  NewRating rating;
  {
    rating.rating = 3.3;
    rating.show = true;
  }

  Country country;
  {
    country.id = 13;
    country.code = "RU";
    country.name = "Россия";
    country.currency.code = "RUB";
    country.currency.sign = "₽";
  }

  PlacesItem item;
  {
    item.location = std::optional<Location>(std::in_place, geopoint);
    item.region = std::optional<Region>(std::in_place, region);
    item.new_rating = std::optional<NewRating>(std::in_place, rating);
    item.type = PlaceType::kMarketplace;
    item.country = std::optional<Country>(std::in_place, country);
    item.business = PlaceBusiness::kStore;
  }

  const auto result = caches::PlacesCacheTraits::Convert(PlacesItem{item});

  ASSERT_TRUE(result.has_value());

  EXPECT_EQ(result->point.value().lat,
            item.location->geo_point.GetLatitudeAsDouble());
  EXPECT_EQ(result->point.value().lon,
            item.location->geo_point.GetLongitudeAsDouble());

  EXPECT_EQ(result->region.id, item.region->id);
  EXPECT_EQ(result->region.geobase_ids, item.region->geobase_ids);
  EXPECT_EQ(result->region.name, item.region->name);
  EXPECT_EQ(result->region.time_zone, item.region->time_zone);

  EXPECT_EQ(result->rating->rating, item.new_rating->rating);
  EXPECT_EQ(result->rating->show, item.new_rating->show);

  EXPECT_EQ(result->type, item.type);

  EXPECT_EQ(result->country->id, item.country->id);
  EXPECT_EQ(result->country->code, item.country->code);
  EXPECT_EQ(result->country->name, item.country->name);
  EXPECT_EQ(result->country->currency.code, item.country->currency.code);
  EXPECT_EQ(result->country->currency.sign, item.country->currency.sign);
  EXPECT_EQ(result->business_type, item.business);
}

TEST(Convert, PlacesCacheTraitsConvertLocationNull) {
  using clients::eats_catalog_storage::NewRating;
  using clients::eats_catalog_storage::PlacesItem;
  using clients::eats_catalog_storage::Region;

  Region region;
  {
    region.id = 2222;
    region.geobase_ids = {1, 2, 3, 4, 5};
    region.time_zone = "Europe/Moscow";
    region.name = "REGION";
  }

  NewRating rating;
  {
    rating.rating = 3.3;
    rating.show = true;
  }

  PlacesItem item;
  {
    item.location = std::nullopt;
    item.region = std::optional<Region>(std::in_place, region);
    item.new_rating = std::optional<NewRating>(std::in_place, rating);
  }

  const auto result = caches::PlacesCacheTraits::Convert(PlacesItem{item});

  ASSERT_TRUE(result.has_value());

  EXPECT_EQ(result->point, std::nullopt);

  EXPECT_EQ(result->region.id, item.region->id);
  EXPECT_EQ(result->region.geobase_ids, item.region->geobase_ids);
  EXPECT_EQ(result->region.name, item.region->name);
  EXPECT_EQ(result->region.time_zone, item.region->time_zone);

  EXPECT_EQ(result->rating->rating, item.new_rating->rating);
  EXPECT_EQ(result->rating->show, item.new_rating->show);
}

TEST(Convert, PlacesCacheTraitsConvertRegionNull) {
  using clients::eats_catalog_storage::Location;
  using clients::eats_catalog_storage::NewRating;
  using clients::eats_catalog_storage::PlacesItem;

  Location geopoint;
  {
    geopoint.geo_point.SetLatitudeFromDouble(123.456);
    geopoint.geo_point.SetLongitudeFromDouble(654.321);
  }

  NewRating rating;
  {
    rating.rating = 3.3;
    rating.show = true;
  }

  PlacesItem item;
  {
    item.location = std::optional<Location>(std::in_place, geopoint);
    item.region = std::nullopt;
    item.new_rating = std::optional<NewRating>(std::in_place, rating);
  }

  ASSERT_ANY_THROW(caches::PlacesCacheTraits::Convert(PlacesItem{item}));
}

TEST(Convert, PlacesCacheTraitsConvertRatingNull) {
  using clients::eats_catalog_storage::Location;
  using clients::eats_catalog_storage::PlacesItem;
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
    region.name = "REGION";
  }

  PlacesItem item;
  {
    item.location = std::optional<Location>(std::in_place, geopoint);
    item.region = std::optional<Region>(std::in_place, region);
    item.new_rating = std::nullopt;
  }

  const auto result = caches::PlacesCacheTraits::Convert(PlacesItem{item});

  ASSERT_TRUE(result.has_value());

  EXPECT_EQ(result->point.value().lat,
            item.location->geo_point.GetLatitudeAsDouble());
  EXPECT_EQ(result->point.value().lon,
            item.location->geo_point.GetLongitudeAsDouble());

  EXPECT_EQ(result->region.id, item.region->id);
  EXPECT_EQ(result->region.geobase_ids, item.region->geobase_ids);
  EXPECT_EQ(result->region.name, item.region->name);
  EXPECT_EQ(result->region.time_zone, item.region->time_zone);

  EXPECT_EQ(result->rating, std::nullopt);
}

TEST(Convert, PlacesCacheTraitsConvertCountryNull) {
  using clients::eats_catalog_storage::PlacesItem;
  using clients::eats_catalog_storage::Region;

  Region region;
  {
    region.id = 2222;
    region.geobase_ids = {1, 2, 3, 4, 5};
    region.time_zone = "Europe/Moscow";
    region.name = "REGION";
  }

  PlacesItem item;
  {
    item.region = std::optional<Region>(std::in_place, region);
    item.country = std::nullopt;
  }

  const auto result = caches::PlacesCacheTraits::Convert(PlacesItem{item});

  ASSERT_TRUE(result.has_value());

  EXPECT_EQ(result->country, std::nullopt);
}
