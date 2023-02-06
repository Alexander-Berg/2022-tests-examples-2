#include <gtest/gtest.h>

#include <cgeohash.h>
#include "views/weathersuggest.hpp"

TEST(Geohash, TestGeohashing) {
  auto morozov =
      views::weathersuggest::internal::Geohash(55.733853, 37.589426, 1000);
  auto metro_station =
      views::weathersuggest::internal::Geohash(55.735183, 37.593286, 1000);
  ASSERT_EQ(morozov, metro_station);

  auto cemetery =
      views::weathersuggest::internal::Geohash(55.724758, 37.554268, 4000);
  ASSERT_TRUE(std::equal(cemetery.begin(), cemetery.end(), morozov.begin()));
}

TEST(Geohash, TestGeohash6AndReverse) {
  std::string geohash;
  const double lat = 55.733853;
  const double lon = 37.589426;
  cgeohash::encode(lat, lon, 6, geohash);

  auto morozov = cgeohash::decode(geohash);
  const double lat_diff = std::abs(lat - morozov.latitude);
  const double lon_diff = std::abs(lon - morozov.longitude);
  ASSERT_TRUE(morozov.latitude_err >= lat_diff);
  ASSERT_TRUE(morozov.longitude_err >= lon_diff);
}

TEST(Geohash, TestGeohash5AndReverse) {
  std::string geohash;
  const double lat = 55.733853;
  const double lon = 37.589426;
  cgeohash::encode(lat, lon, 5, geohash);

  auto morozov = cgeohash::decode(geohash);
  const double lat_diff = std::abs(lat - morozov.latitude);
  const double lon_diff = std::abs(lon - morozov.longitude);
  ASSERT_TRUE(morozov.latitude_err >= lat_diff);
  ASSERT_TRUE(morozov.longitude_err >= lon_diff);
}
