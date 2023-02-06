#include <geometry/bounding_box.hpp>

#include <gtest/gtest.h>

#include <geometry/test/geometry_plugin_test.hpp>

using geometry::BoundingBox;
using geometry::lat;
using geometry::lon;
using geometry::Position;
using geometry::test::GeometryTestPlugin;

TEST(BoundingBox, Constructors) {
  BoundingBox bbox({10.0 * lon, 12.0 * lat}, {11.0 * lon, 11.0 * lat});
  GeometryTestPlugin::TestPositionsAreClose(bbox.south_west,
                                            {10.0 * lon, 11.0 * lat});
  GeometryTestPlugin::TestPositionsAreClose(bbox.north_east,
                                            {11.0 * lon, 12.0 * lat});
}

TEST(BoundingBox, Operators) {
  BoundingBox bbox_1({4. * lon, 20.69 * lat}, {69. * lon, 4.20 * lat});
  BoundingBox bbox_2({4. * lon, 69. * lat}, {20.69 * lon, 20.69 * lat});
  EXPECT_FALSE(geometry::AreCloseBoundingBoxes(bbox_1, bbox_2));

  bbox_1 = bbox_2;
  EXPECT_TRUE(geometry::AreCloseBoundingBoxes(bbox_1, bbox_2));
}

TEST(BoundingBox, Normalize) {
  BoundingBox bbox;

  bbox.south_west = {2. * lon, 2.0 * lat};
  bbox.north_east = {1. * lon, 1.0 * lat};

  bbox.Normalize();
  GeometryTestPlugin::TestPositionsAreClose(bbox.south_west,
                                            {2. * lon, 1. * lat});
  GeometryTestPlugin::TestPositionsAreClose(bbox.north_east,
                                            {1. * lon, 2. * lat});
}

TEST(BoundingBox, Contains) {
  BoundingBox bbox({10. * lon, 20.0 * lat}, {11. * lon, 22 * lat});

  EXPECT_TRUE(bbox.Contains({10.5 * lon, 20.1 * lat}));
  EXPECT_FALSE(bbox.Contains({9.0 * lon, 20.1 * lat}));
  EXPECT_FALSE(bbox.Contains({10.5 * lon, -19.0 * lat}));

  // anti-meridian crossing bbox
  bbox = BoundingBox({179 * lon, 22.0 * lat}, {-175 * lon, 20.0 * lat});
  EXPECT_TRUE(bbox.CrossesAntimeridian());
  EXPECT_TRUE(bbox.Contains({179.5 * lon, 21.0 * lat}));
  EXPECT_TRUE(bbox.Contains({-176. * lon, 21.0 * lat}));
  EXPECT_FALSE(bbox.Contains({-174. * lon, 21.0 * lat}));
  EXPECT_FALSE(bbox.Contains({-174. * lon, 21.0 * lat}));
  EXPECT_FALSE(bbox.Contains(
      {std::numeric_limits<double>::infinity() * lon, 21.0 * lat}));
  EXPECT_FALSE(bbox.Contains(
      {-179.5 * lon, std::numeric_limits<double>::infinity() * lat}));
}

TEST(BoundingBox, GeometricalCenter) {
  using namespace ::geometry::literals;
  BoundingBox bbox({10. * lon, 20.0 * lat}, {12. * lon, 24 * lat});

  EXPECT_EQ(Position(11.0_lon, 22.0_lat), bbox.GeometricalCenter());
  EXPECT_TRUE(bbox.Contains(bbox.GeometricalCenter()));

  // anti-meridian crossing bbox
  bbox = BoundingBox({179 * lon, 20.0 * lat}, {-177 * lon, 24.0 * lat});
  EXPECT_EQ((Position{-179.0_lon, 22.0_lat}), bbox.GeometricalCenter());
  EXPECT_TRUE(bbox.Contains(bbox.GeometricalCenter()));

  // anti-meridian crossing bbox
  bbox = BoundingBox({173 * lon, 20.0 * lat}, {-177 * lon, 24.0 * lat});
  EXPECT_EQ((Position{178.0_lon, 22.0_lat}), bbox.GeometricalCenter());
  EXPECT_TRUE(bbox.Contains(bbox.GeometricalCenter()));

  // A few verified samples
  {
    geometry::BoundingBox bbox({179 * lon, 55.1 * lat},
                               {-178 * lon, 55.2 * lat});
    ASSERT_TRUE(geometry::AreClosePositions(
        bbox.GeometricalCenter(),
        geometry::Position{-179.5 * geometry::lon, 55.15 * geometry::lat}));
  }
  {
    geometry::BoundingBox bbox({177 * lon, 55.1 * lat},
                               {-178 * lon, 55.2 * lat});
    ASSERT_TRUE(geometry::AreClosePositions(
        bbox.GeometricalCenter(),
        geometry::Position{179.5 * geometry::lon, 55.15 * geometry::lat}));
  }
  {
    geometry::BoundingBox bbox({177 * lon, 55.1 * lat},
                               {173 * lon, 55.2 * lat});
    bbox.north_east.longitude = 173 * geometry::lon;
    ASSERT_TRUE(geometry::AreClosePositions(
        bbox.GeometricalCenter(),
        geometry::Position{-5.0 * geometry::lon, 55.15 * geometry::lat}));
  }
  {
    geometry::BoundingBox bbox({172 * lon, 55.1 * lat},
                               {173 * lon, 55.2 * lat});
    ASSERT_TRUE(geometry::AreClosePositions(
        bbox.GeometricalCenter(),
        geometry::Position{172.5 * geometry::lon, 55.15 * geometry::lat}));
  }
}
