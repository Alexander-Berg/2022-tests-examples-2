#include <geometry/viewport.hpp>

#include <gtest/gtest.h>

#include <geometry/position.hpp>
#include <geometry/test/geometry_plugin_test.hpp>

using geometry::lat;
using geometry::lon;
using geometry::Viewport;

TEST(Viewport, Constructors) {
  Viewport::BaseType p_alpha(4. * lon, 4.20 * lat),
      p_beta(69. * lon, 20.69 * lat);
  Viewport v(p_alpha, p_beta);
  EXPECT_TRUE(geometry::AreClosePositions(v.top_left, {4. * lon, 20.69 * lat}));
  EXPECT_TRUE(
      geometry::AreClosePositions(v.bottom_right, {69. * lon, 4.20 * lat}));

  v = Viewport({4. * lon, 4.20 * lat}, {69. * lon, 20.69 * lat});
  EXPECT_TRUE(geometry::AreClosePositions(v.top_left, {4. * lon, 20.69 * lat}));
  EXPECT_TRUE(
      geometry::AreClosePositions(v.bottom_right, {69. * lon, 4.20 * lat}));
}

TEST(Viewport, Operators) {
  Viewport v_alpha({4. * lon, 20.69 * lat}, {69. * lon, 4.20 * lat});
  Viewport v_beta({4. * lon, 69. * lat}, {20.69 * lon, 20.69 * lat});
  EXPECT_FALSE(geometry::AreCloseViewports(v_alpha, v_beta));

  v_alpha = v_beta;
  EXPECT_TRUE(geometry::AreCloseViewports(v_alpha, v_beta));

  const auto bgb = Viewport::BGBox(v_beta);
  EXPECT_TRUE(
      geometry::AreClosePositions(bgb.min_corner(), {4. * lon, 69. * lat}));
  EXPECT_TRUE(geometry::AreClosePositions(bgb.max_corner(),
                                          {20.69 * lon, 20.69 * lat}));
}

TEST(Viewport, Normalize) {
  Viewport v;

  v.top_left = {69. * lon, 4.20 * lat};
  v.bottom_right = {4. * lon, 20.69 * lat};
  EXPECT_TRUE(geometry::AreClosePositions(v.top_left, {69. * lon, 4.20 * lat}));
  EXPECT_TRUE(
      geometry::AreClosePositions(v.bottom_right, {4. * lon, 20.69 * lat}));

  v.Normalize();
  EXPECT_TRUE(geometry::AreClosePositions(v.top_left, {4. * lon, 20.69 * lat}));
  EXPECT_TRUE(
      geometry::AreClosePositions(v.bottom_right, {69. * lon, 4.20 * lat}));
}

TEST(Viewport, Center) {
  Viewport v({10. * lon, 10. * lat}, {20. * lon, 20. * lat});
  EXPECT_TRUE(geometry::AreClosePositions(v.Center(), {15. * lon, 15. * lat}));

  v = Viewport({10. * lon, 10. * lat}, {5. * lon, 5. * lat});
  EXPECT_TRUE(geometry::AreClosePositions(v.Center(), {7.5 * lon, 7.5 * lat}));

  v = Viewport({5. * lon, 5. * lat}, {5. * lon, 5. * lat});
  EXPECT_TRUE(geometry::AreClosePositions(v.Center(), {5. * lon, 5. * lat}));
}

TEST(Viewport, Contains) {
  Viewport v({4. * lon, 20.69 * lat}, {69. * lon, 4.20 * lat});

  EXPECT_FALSE(v.Contains({0. * lon, 0. * lat}));
  EXPECT_FALSE(v.Contains({4. * lon, 0. * lat}));
  EXPECT_FALSE(v.Contains({30. * lon, 0. * lat}));
  EXPECT_FALSE(v.Contains({30. * lon, 25. * lat}));
  EXPECT_FALSE(v.Contains({69. * lon, 21. * lat}));
  EXPECT_FALSE(v.Contains({70. * lon, 20.69 * lat}));

  EXPECT_TRUE(v.Contains({4. * lon, 20.69 * lat}));
  EXPECT_TRUE(v.Contains({4. * lon, 4.20 * lat}));
  EXPECT_TRUE(v.Contains({4. * lon, 4.20 * lat}));
  EXPECT_TRUE(v.Contains({69. * lon, 4.20 * lat}));

  EXPECT_TRUE(v.Contains({30. * lon, 10. * lat}));
}

TEST(Viewport, ToBGBox) {
  auto v = geometry::test::GeometryTestPlugin::CreateViewport(10, 20);
  const auto bgb = Viewport::BGBox(v);
  EXPECT_TRUE(geometry::AreClosePositions(v.top_left, bgb.min_corner()));
  EXPECT_TRUE(geometry::AreClosePositions(v.bottom_right, bgb.max_corner()));
}
