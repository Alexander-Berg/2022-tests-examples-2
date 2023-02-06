#include <gtest/gtest.h>
#include <ml/common/features/features.hpp>
#include <ml/common/geohash.hpp>
#include <ml/common/geopoint.hpp>

TEST(CommonGeohash, encode) {
  ml::common::GeoPoint geopoint{37, 55};
  auto result = ml::common::GeohashEncode(geopoint, 10);
  ASSERT_EQ(result, "ucf2cuqw4r");
}

TEST(CommonGeohash, features) {
  ml::common::GeoPoint geopoint{37, 55};
  std::vector<std::string> features;
  ml::common::features::AddGeohashes(features, geopoint, 2, 5);
  std::vector<std::string> expected_features{"uc", "ucf", "ucf2", "ucf2c"};
  ASSERT_EQ(features, expected_features);
}
