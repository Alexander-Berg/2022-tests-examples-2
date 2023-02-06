#include <gtest/gtest.h>

#include <climits>
#include <cmath>

#include <models/geometry/distance.hpp>

using models::geometry::CalcDistance;
using models::geometry::CalcDistanceApproximation;
using models::geometry::Point;

namespace {

class DistanceParams
    : public testing::Test,
      public testing::WithParamInterface<std::pair<Point, Point>> {};

}  // namespace

TEST_P(DistanceParams, One) {
  const auto& param = GetParam();

  const int d0 = CalcDistance(param.first, param.second);
  const int d1 = CalcDistanceApproximation(param.first, param.second);

  if (d1 == 0)
    EXPECT_EQ(d0, d1);
  else
    EXPECT_GT(0.001, std::abs(1.0 - (1.0 * d0 / d1)));  // 0,1% dif

  EXPECT_EQ(d1, CalcDistanceApproximation({param.first, param.second}));
}

INSTANTIATE_TEST_SUITE_P(
    Serial, DistanceParams,
    testing::Values(
        std::make_pair(Point(0.0, 0.0), Point(0.0, 0.0)),
        std::make_pair(Point(0.0, 0.0), Point(0.000001, 0.000001)),
        std::make_pair(Point(0.0, 0.0), Point(0.00001, 0.00001)),
        std::make_pair(Point(0.0, 0.0), Point(0.0001, 0.0001)),
        std::make_pair(Point(0.0, 0.0), Point(0.001, 0.001)),
        std::make_pair(Point(0.0, 0.0), Point(0.01, 0.01)),
        std::make_pair(Point(0.0, 0.0), Point(0.1, 0.1)),
        std::make_pair(Point(0.0, 0.0), Point(1.0, 1.0)),
        std::make_pair(Point(37.0, 55.0), Point(37.0, 55.0)),
        std::make_pair(Point(37.0, 55.0), Point(37.000001, 55.000001)),
        std::make_pair(Point(37.0, 55.0), Point(37.00001, 55.00001)),
        std::make_pair(Point(37.0, 55.0), Point(37.0001, 55.0001)),
        std::make_pair(Point(37.0, 55.0), Point(37.001, 55.001)),
        std::make_pair(Point(37.0, 55.0), Point(37.01, 55.01)),
        std::make_pair(Point(37.0, 55.0), Point(37.1, 55.1)),
        std::make_pair(Point(37.0, 55.0), Point(38.0, 56.0))));

TEST(Distance, EmptyPoint) {
  Point empty;
  EXPECT_EQ(CalcDistance(empty, empty), INT_MAX);
  EXPECT_EQ(CalcDistanceApproximation(empty, empty), INT_MAX);
  Point non_empty(55.0, 33.0);
  EXPECT_EQ(CalcDistance(empty, non_empty), INT_MAX);
  EXPECT_EQ(CalcDistanceApproximation(empty, non_empty), INT_MAX);
  EXPECT_LT(CalcDistance(non_empty, non_empty), INT_MAX);
  EXPECT_LT(CalcDistanceApproximation(non_empty, non_empty), INT_MAX);
}

TEST(Distance, Path) {
  Point p0(37.0, 55.0);
  Point p1(37.1, 55.1);
  Point p2(37.2, 55.2);
  EXPECT_EQ(
      CalcDistanceApproximation(p0, p1) + CalcDistanceApproximation(p1, p2),
      CalcDistanceApproximation({p0, p1, p2}));
}
