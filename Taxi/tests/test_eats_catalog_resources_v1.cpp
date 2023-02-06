#include <gtest/gtest.h>

#include <sstream>

#include <ml/common/filesystem.hpp>
#include <ml/eats/catalog/resources/v1.hpp>

#include "common/utils.hpp"

namespace {
const std::string kTestDataDir =
    tests::common::GetTestResourcePath("eats_catalog_resources_v1");
}  // namespace

TEST(EatsCatalogResourcesV0, parse_promo_info) {
  auto obj =
      ml::common::FromJsonString<ml::eats::catalog::resources::v1::PromoInfo>(
          ml::common::ReadFileContents(kTestDataDir +
                                       "/promo_info_example.json"));
  ASSERT_EQ(obj.place_id, 16);
  ASSERT_EQ(obj.started_at,
            ml::common::datetime::Stringtime("2019-01-01T00:00:00Z"));
  ASSERT_EQ(obj.finished_at,
            ml::common::datetime::Stringtime("2019-01-10T00:00:00Z"));
}

TEST(EatsCatalogResourcesV0, parse_place_info) {
  auto obj =
      ml::common::FromJsonString<ml::eats::catalog::resources::v1::PlaceInfo>(
          ml::common::ReadFileContents(kTestDataDir +
                                       "/place_info_example.json"));
  ASSERT_EQ(obj.id, 1);
  ASSERT_EQ(obj.average_rating_count, 20);
  ASSERT_DOUBLE_EQ(obj.average_rating_value, 4.3);
  ASSERT_EQ(obj.brand_id, 168);
  ASSERT_EQ(obj.slug, "имя");
  ASSERT_EQ(obj.price_category_id, 4);
  ASSERT_DOUBLE_EQ(obj.location.lon, 57.5);
  ASSERT_DOUBLE_EQ(obj.location.lat, 43.2);
  std::vector<int64_t> vec = {1, 2, 3};
  ASSERT_EQ(obj.place_category_ids, vec);
}

TEST(EatsCatalogResourcesV0, load_static_resources) {
  auto storage = ml::eats::catalog::resources::v1::LoadStaticResourcesFromDir(
      kTestDataDir + "/static_resources");
  ml::eats::catalog::resources::v1::PlaceInfo default_info{};
  ASSERT_EQ(storage.GetPlaceInfo(0), std::nullopt);
  ASSERT_EQ(storage.GetPlaceInfo(1, default_info)->id, 1);
  ASSERT_EQ(storage.GetPlaceInfo(2, default_info)->id, 2);

  using ml::common::datetime::Stringtime;
  ASSERT_FALSE(storage.HasPromo(1, Stringtime("2018-12-31T23:59:59Z")));
  ASSERT_TRUE(storage.HasPromo(1, Stringtime("2019-01-01T00:00:00Z")));
  ASSERT_FALSE(storage.HasPromo(1, Stringtime("2019-01-11T00:00:00Z")));
  ASSERT_TRUE(storage.HasPromo(1, Stringtime("2019-01-12T00:00:00Z")));
  ASSERT_FALSE(storage.HasPromo(1, Stringtime("2019-01-30T00:00:00Z")));

  ASSERT_FALSE(storage.HasPromo(2, Stringtime("2019-01-19T00:00:00Z")));
  ASSERT_TRUE(storage.HasPromo(2, Stringtime("2019-01-20T00:00:00Z")));
  ASSERT_FALSE(storage.HasPromo(2, Stringtime("2019-01-23T00:00:00Z")));

  ASSERT_EQ(storage.GetPlaceExternalInfo(0), std::nullopt);
  ASSERT_EQ(storage.GetPlaceExternalInfo(1)->id, 1);

  ASSERT_EQ(storage.GetUserExternalInfo(0), std::nullopt);
  ASSERT_EQ(storage.GetUserExternalInfo(1)->id, 1);
}
