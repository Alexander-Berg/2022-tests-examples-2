#include <gtest/gtest.h>

#include <models/geometry/distance.hpp>
#include <models/geometry/viewport.hpp>

using models::geometry::CalcDistance;
using models::geometry::CalcViewport;
using models::geometry::Point;
using models::geometry::Viewport;

namespace {

struct CalcViewportParam {
  int radius;
  Point point;
};

class CalcViewportParams
    : public testing::Test,
      public testing::WithParamInterface<CalcViewportParam> {};

}  // namespace

TEST(Viewport, GetCenter) {
  EXPECT_TRUE(Viewport{}.GetCenter().empty());
  EXPECT_EQ(Point(1.0, 1.0), Viewport({1.0, 1.0}, {1.0, 1.0}).GetCenter());
  EXPECT_EQ(Point(1.0, 1.0), Viewport({0.0, 0.0}, {2.0, 2.0}).GetCenter());
}

TEST(Viewport, Contains) {
  EXPECT_FALSE(Viewport{}.Contains({}));
  EXPECT_FALSE(Viewport{}.Contains({1.0, 1.0}));
  EXPECT_FALSE(Viewport({0.0, 0.0}, {2.0, 2.0}).Contains({}));
  EXPECT_FALSE(Viewport({0.0, 0.0}, {2.0, 2.0}).Contains({3.0, 3.0}));

  EXPECT_TRUE(Viewport({0.0, 0.0}, {2.0, 2.0}).Contains({1.0, 1.0}));
}

TEST(Viewport, empty) {
  EXPECT_TRUE(Viewport{}.empty());
  EXPECT_TRUE(Viewport({}, {2.0, 2.0}).empty());
  EXPECT_TRUE(Viewport({0.0, 0.0}, {}).empty());

  EXPECT_FALSE(Viewport({0.0, 0.0}, {2.0, 2.0}).empty());
}

TEST(Viewport, Normalize) {
  Viewport vp({0.0, 0.0}, {2.0, 2.0});
  EXPECT_LE(vp.top_left.lon, vp.bottom_right.lon);
  EXPECT_GE(vp.top_left.lat, vp.bottom_right.lat);
}

TEST_P(CalcViewportParams, One) {
  const auto& param = GetParam();

  const auto viewport = CalcViewport(param.point, param.radius);
  auto normalized = viewport;
  normalized.Normalize();
  const auto center = viewport.GetCenter();

  EXPECT_EQ(CalcDistance(center, viewport.GetCenter()), 0);
  EXPECT_EQ(normalized.top_left, viewport.top_left);
}

INSTANTIATE_TEST_SUITE_P(
    Serial, CalcViewportParams,
    testing::Values(CalcViewportParam{0, Point(0, 0)},
                    CalcViewportParam{0, Point(0.000001, 0.000001)},
                    CalcViewportParam{1, Point(0.000001, 0.000001)},
                    CalcViewportParam{10, Point(0.01, 0.01)},
                    CalcViewportParam{10, Point(37.0, 55.0)},
                    CalcViewportParam{10000, Point(37.0, 55.0)},
                    CalcViewportParam{10, Point(55.0, 37.0)},
                    CalcViewportParam{10000, Point(55.0, 37.0)}));
