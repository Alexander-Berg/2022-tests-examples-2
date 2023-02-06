#include <gtest/gtest.h>

#include <models/geometry/distance.hpp>
#include <models/geometry/viewport.hpp>

#include <client-zone-geoindex/models/geohash/geohash_iter.hpp>

#include <set>

namespace gh = client_zone_geoindex::models::geohash;
namespace czgm = client_zone_geoindex::models;

struct GeohashIteratorParam {
  ::models::geometry::Point point;
  int radius;
  std::set<std::string> expected;
};

class GeohashIterator : public ::testing::TestWithParam<GeohashIteratorParam> {
};

TEST_P(GeohashIterator, Test) {
  static const int kGeohashPrecision = 5;
  const auto& viewport =
      ::models::geometry::CalcViewport(GetParam().point, GetParam().radius);

  std::set<std::string> hashes;
  for (auto iter = gh::BBoxIterator(viewport.top_left, viewport.bottom_right,
                                    kGeohashPrecision);
       !iter.Terminated(); ++iter) {
    hashes.insert(iter.Hash());
  }

  ASSERT_EQ(hashes, GetParam().expected);
}

// cell size 5x5km with geohash precision == 5
// -4.329, 48.669 is in center of gbsuv cell
// neighbours
// gbsv5 gbsvh	gbsvj	gbsvn gbsvp
// gbsug gbsuu	gbsuv	gbsuy gbsuz
// gbsue gbsus	gbsut	gbsuw gbsux

INSTANTIATE_TEST_SUITE_P(GeohashIterator, GeohashIterator,
                         ::testing::Values(
                             GeohashIteratorParam{
                                 ::models::geometry::Point(-4.329, 48.669),
                                 10,
                                 {"gbsuv"},
                             },
                             GeohashIteratorParam{
                                 ::models::geometry::Point(-4.329, 48.669),
                                 1000,
                                 {"gbsuv"},
                             },
                             GeohashIteratorParam{
                                 ::models::geometry::Point(-4.329, 48.669),
                                 3000,
                                 {"gbsus", "gbsut", "gbsuu", "gbsuv", "gbsuw",
                                  "gbsuy", "gbsvh", "gbsvj", "gbsvn"},
                             },
                             GeohashIteratorParam{
                                 ::models::geometry::Point(-4.329, 48.669),
                                 5000,
                                 {"gbsue", "gbsug", "gbsus", "gbsut", "gbsuu",
                                  "gbsuv", "gbsuw", "gbsux", "gbsuy", "gbsuz",
                                  "gbsv5", "gbsvh", "gbsvj", "gbsvn", "gbsvp"},
                             }));
