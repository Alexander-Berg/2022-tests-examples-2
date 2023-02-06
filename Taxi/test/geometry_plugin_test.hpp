#pragma once

#include <geometry/cartesian_polygon.hpp>
#include <geometry/position.hpp>
#include <geometry/test/geometry_generator.hpp>
#include <geometry/viewport.hpp>

#include <gtest/gtest.h>

#include <fmt/format.h>

namespace geometry::test {

/// This plugin extends geometry::test::GeometryPlugin with comparison
/// methods. Those methods employ EXPECT_* family of macroses internally
class GeometryTestPlugin : public GeometryGenerator {
 public:
  static const constexpr double kCoordCloseThreshold = 0.000001;
  static const constexpr double kDirectionCloseThreshold = 0.5;  // degree

  /// Tests that positions are close enough for testing purposes
  static void TestPositionsAreClose(const ::geometry::Position& first,
                                    const ::geometry::Position& second);
  /// Tests that viewports are close enough for testing purposes
  static void TestViewportsAreClose(const ::geometry::Viewport& first,
                                    const ::geometry::Viewport& second);
  /// Tests that bounding boxes are close enough for testing purposes
  static void TestBoundingBoxesAreClose(const ::geometry::BoundingBox& first,
                                        const ::geometry::BoundingBox& second);
  /// Tests that polygons are close enough for testing purposes
  static void TestCartesianPolygonsAreClose(
      const ::geometry::CartesianPolygon& first,
      const ::geometry::CartesianPolygon& second);
  /// Tests that latitudes are close enough for testing purposes.
  static void TestLatitudesAreClose(const ::geometry::Latitude lat1,
                                    const ::geometry::Latitude lat2) {
    EXPECT_NEAR(lat1.value(), lat2.value(), kCoordCloseThreshold);
  }

  /// Tests that longitudes are close enough for testing purposes.
  static void TestLongitudesAreClose(const ::geometry::Longitude lon1,
                                     const ::geometry::Longitude lon2) {
    EXPECT_NEAR(lon1.value(), lon2.value(), kCoordCloseThreshold);
  }

  /// Tests that directions are close enough for testing purposes
  static void TestDirectionsAreClose(const ::geometry::Azimuth direction1,
                                     const ::geometry::Azimuth direction2) {
    EXPECT_NEAR(direction1.value(), direction2.value(),
                kDirectionCloseThreshold);
  }

  /// Tests that positions are close enough for testing purposes
  static void TestPositionsAreClose(
      const std::vector<::geometry::Position>& first,
      const std::vector<::geometry::Position>& second);

  void PluginSetUp() {}
  void PluginTearDown() {}
  static void PluginSetUpTestSuite() {}
  static void PluginTearDownTestSuite() {}
};

inline void GeometryTestPlugin::TestPositionsAreClose(
    const ::geometry::Position& first, const ::geometry::Position& second) {
  SCOPED_TRACE(__FUNCTION__);
  if (first.IsFinite() && second.IsFinite()) {
    TestLatitudesAreClose(first.latitude, second.latitude);
    TestLongitudesAreClose(first.longitude, second.longitude);
  } else if (!first.IsFinite() && !second.IsFinite()) {
    // two nowhere positions are equal
  } else {
    FAIL();
  }
}

inline void GeometryTestPlugin::TestViewportsAreClose(
    const ::geometry::Viewport& first, const ::geometry::Viewport& second) {
  SCOPED_TRACE(__FUNCTION__);
  TestPositionsAreClose(first.top_left, second.top_left);
  TestPositionsAreClose(first.bottom_right, second.bottom_right);
}

inline void GeometryTestPlugin::TestBoundingBoxesAreClose(
    const ::geometry::BoundingBox& first,
    const ::geometry::BoundingBox& second) {
  SCOPED_TRACE(__FUNCTION__);
  TestPositionsAreClose(first.south_west, second.south_west);
  TestPositionsAreClose(first.north_east, second.north_east);
}

inline void GeometryTestPlugin::TestCartesianPolygonsAreClose(
    const ::geometry::CartesianPolygon& first,
    const ::geometry::CartesianPolygon& second) {
  SCOPED_TRACE(__FUNCTION__);
  ASSERT_EQ(first.outer().size(), second.outer().size());
  for (size_t i = 0; i < first.outer().size(); i++) {
    SCOPED_TRACE(__FUNCTION__ + fmt::format(" at {}", i));
    TestPositionsAreClose(first.outer()[i], second.outer()[i]);
  }
}

inline void GeometryTestPlugin::TestPositionsAreClose(
    const std::vector<::geometry::Position>& first,
    const std::vector<::geometry::Position>& second) {
  ASSERT_EQ(first.size(), second.size());
  for (size_t i = 0; i < first.size(); i++) {
    SCOPED_TRACE(__FUNCTION__ + fmt::format(" at {}", i));
    TestPositionsAreClose(first[i], second[i]);
  }
}

}  // namespace geometry::test
