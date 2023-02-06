#include <gtest/gtest.h>

#include <models/geometry/point.hpp>

using models::geometry::Point;

TEST(Point, Empty) {
  Point empty;
  EXPECT_TRUE(empty.empty());
  empty = Point(1.0, NAN);
  EXPECT_TRUE(empty.empty());
  empty = Point(NAN, 1.0);
  EXPECT_TRUE(empty.empty());
  empty = Point(1.0, 1.0);
  EXPECT_FALSE(empty.empty());
}

TEST(Point, Legacy) {
  std::vector<double> point_array;
  point_array.push_back(0);
  point_array.push_back(0);
  Point point(point_array);
  EXPECT_TRUE(std::isnan(point.lon));
  EXPECT_TRUE(std::isnan(point.lat));
}
