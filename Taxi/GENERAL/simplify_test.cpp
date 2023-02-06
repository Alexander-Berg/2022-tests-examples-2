#include <geometry/simplify.hpp>

#include <gtest/gtest.h>

namespace geometry {

TEST(SimplifyPolylineTest, Simple) {
  std::vector<Position> track{{10 * lon, 20 * lat},
                              {10 * lon, 30 * lat},
                              {0 * lon, 40 * lat},
                              {0 * lon, 20 * lat}};

  auto simplified_track = SimplifyGeoTrack(track, 3);

  EXPECT_EQ(simplified_track.size(), 3);
  EXPECT_EQ(simplified_track[0], Position(10 * lon, 20 * lat));
  EXPECT_EQ(simplified_track[1], Position(0 * lon, 40 * lat));
  EXPECT_EQ(simplified_track[2], Position(0 * lon, 20 * lat));
}

}  // namespace geometry
