#include <gtest/gtest.h>

#include <models/polygon.hpp>

using price_calc::models::Point;
using price_calc::models::Polygon;

struct ContainsPointTestData {
  const Polygon polygon;
  const Point point;
  const bool contains;
};

class PolygonTest : public ::testing::TestWithParam<ContainsPointTestData> {};

TEST_P(PolygonTest, PointIsInside) {
  EXPECT_EQ(GetParam().polygon.Contains(GetParam().point), GetParam().contains);
}

namespace {

static const Polygon kPolygon1({Point{3, 6}, Point{6, 1}, Point{10, 4}}, 0);
static const Polygon kPolygon2({Point{3, 6}, Point{10, 4}, Point{6, 1},
                                Point{6, 2}, Point{8, 4}, Point{0, 5}},
                               0);
static const Polygon kPolygon3({Point{7, 5}, Point{10, 9}, Point{13, 2}}, 10);

}  // namespace

INSTANTIATE_TEST_SUITE_P(
    PolygonTest, PolygonTest,
    ::testing::Values(ContainsPointTestData{kPolygon1, Point{3, 4}, false},
                      ContainsPointTestData{kPolygon1, Point{7, 4}, true},
                      ContainsPointTestData{kPolygon2, Point{7, 4}, false},
                      ContainsPointTestData{kPolygon2, Point{9, 4}, true},
                      ContainsPointTestData{kPolygon2, Point{7, 4.1}, false},
                      ContainsPointTestData{kPolygon2, Point{9, 4.1}, true},
                      ContainsPointTestData{kPolygon2, Point{2, 5}, true},
                      ContainsPointTestData{kPolygon2, Point{5.9, 1.5}, false},
                      ContainsPointTestData{kPolygon2, Point{6.1, 1.5}, true},
                      ContainsPointTestData{kPolygon2, Point{5.9, 2}, false},
                      ContainsPointTestData{kPolygon2, Point{6.1, 2}, true},
                      ContainsPointTestData{kPolygon3, Point{4, 2}, false},
                      ContainsPointTestData{kPolygon3, Point{13, 2}, true}));
