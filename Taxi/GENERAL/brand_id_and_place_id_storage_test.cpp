#include <gtest/gtest.h>

#include <userver/dump/test_helpers.hpp>
#include "brand_id_and_place_id_storage.hpp"

TEST(ReadWrite, StrongTypedefPlaceIdDump) {
  models::PlaceId test_value{"1234"};

  auto writed = dump::ToBinary<models::PlaceId>(test_value);
  auto readed = dump::FromBinary<models::PlaceId>(writed);

  EXPECT_EQ(test_value, readed);
}

TEST(ReadWrite, StrongTypedefBrandIdDump) {
  models::BrandId test_value{"123874"};

  auto writed = dump::ToBinary<models::BrandId>(test_value);
  auto readed = dump::FromBinary<models::BrandId>(writed);

  EXPECT_EQ(test_value, readed);
}

TEST(ReadWrite, PlaceFromCatalogStorageDump) {
  caches::RelatedRestaurantsBrandId test_value = {models::PlaceId{"173337"},
                                                  models::BrandId{"234"}};

  auto writed = dump::ToBinary<caches::RelatedRestaurantsBrandId>(test_value);
  auto readed = dump::FromBinary<caches::RelatedRestaurantsBrandId>(writed);

  EXPECT_EQ(test_value.place_id, readed.place_id);
  EXPECT_EQ(test_value.brand_id, readed.brand_id);
}

TEST(Convert, PlacesCacheTraitsConvert) {
  using clients::eats_catalog_storage::PlacesItem;

  PlacesItem item;
  item.id = 1988;
  item.brand = std::optional<::clients::eats_catalog_storage::Brand>(
      ::clients::eats_catalog_storage::Brand{12, "", ""});

  auto result =
      caches::RelatedRestaurantsCacheTraits::Convert(PlacesItem{item});

  ASSERT_TRUE(result.has_value());

  EXPECT_EQ(result->place_id.GetUnderlying(), std::to_string(item.id));
  EXPECT_EQ(result->brand_id.GetUnderlying(), std::to_string(item.brand->id));

  item.brand = std::nullopt;
  result = caches::RelatedRestaurantsCacheTraits::Convert(PlacesItem{item});

  ASSERT_TRUE(!result.has_value());
}
