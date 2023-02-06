#include <gtest/gtest.h>

#include "geohash/geohash.hpp"
#include "utils/geometry.hpp"

#include <random>

class DataElement : public utils::geometry::Point {
 public:
  using utils::geometry::Point::Point;

  cgeohash::DecodedBBox GetBBox() const {
    return cgeohash::DecodedBBox{lat, lon, lat, lon};
  }
};

class Filter : public utils::geohash::DataFilter<DataElement> {
  virtual bool Satisfy(const DataElement* data_element, double radius,
                       const utils::geometry::Point& center) const {
    return CalcDistance(*data_element, center) <= radius;
  }

  virtual bool Satisfy(const DataElement* data_element,
                       const utils::geometry::Viewport& v) const {
    return utils::geometry::WithinRect(*data_element, v);
  }
};

TEST(geohash, one_element) {
  std::vector<DataElement> points({DataElement{37.593614, 55.741567}});

  utils::geohash::GeoHash<DataElement> geo_hash(points);
  auto res_points = geo_hash.radius_search(1, {37.593614, 55.741567}, Filter());
  ASSERT_EQ(1u, res_points.size());
}

TEST(geohash, radius_search) {
  std::vector<DataElement> data;

  std::default_random_engine generator;
  std::uniform_real_distribution<double> lat_d(55, 56);
  std::uniform_real_distribution<double> lon_d(37, 38);

  for (int i = 0; i < 10000; ++i) {
    data.push_back(DataElement{lat_d(generator), lon_d(generator)});
  }
  utils::geohash::GeoHash<DataElement> geo_hash(data);
  for (int i = 0; i < 1000; ++i) {
    auto center = utils::geometry::Point{lat_d(generator), lon_d(generator)};
    auto points = geo_hash.radius_search(1000, center, Filter());
    for (auto point : points) {
      ASSERT_LE(utils::geometry::CalcDistance(*point, center), 1000.);
    }
  }

  auto zero_radius_search = geo_hash.radius_search(
      0.000001, utils::geometry::Point{lat_d(generator), lon_d(generator)},
      Filter());
  ASSERT_EQ(zero_radius_search.size(), 0u);

  auto zero_points_search =
      geo_hash.radius_search(1000, utils::geometry::Point{50, 50}, Filter());
  ASSERT_EQ(zero_points_search.size(), 0u);
}

TEST(geohash, nearest_search) {
  std::vector<DataElement> data;

  std::default_random_engine generator;
  std::uniform_real_distribution<double> lat_d(55, 56);
  std::uniform_real_distribution<double> lon_d(37, 38);

  for (int i = 0; i < 10000; ++i) {
    data.push_back(DataElement{lon_d(generator), lat_d(generator)});
  }
  utils::geohash::GeoHash<DataElement> geo_hash(data);

  for (int i = 0; i < 1000; ++i) {
    auto center = DataElement{37.5, 55.5};
    auto points = geo_hash.nearest_search(10, 10000, center, Filter());

    ASSERT_GE(10u, points.size());
    for (auto point : points) {
      ASSERT_GE(10000., utils::geometry::CalcDistance(*point, center));
    }
  }

  auto zero_points_search = geo_hash.nearest_search(
      10, 1000, utils::geometry::Point{50, 50}, Filter());
  ASSERT_EQ(zero_points_search.size(), 0u);
}
