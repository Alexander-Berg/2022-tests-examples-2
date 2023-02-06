#pragma once

#include <geometry/bounding_box.hpp>
#include <geometry/cartesian_polygon.hpp>
#include <geometry/position.hpp>
#include <geometry/viewport.hpp>

namespace geometry::test {

/// This plugin provides functions geo positions/signals etc.
/// Passing same salt will result in same value
/// All double/float members are created with integer values to allow comparison
/// with '=='
/// This plugin must not depend from google test
/// It can be used both in google tests and in google benchmarks
class GeometryGenerator {
 public:
  /// Calling with same argument will provide same result
  static ::geometry::Latitude CreateLatitude(const size_t salt) {
    return (static_cast<double>(((salt % 100) * 10 + salt / 2) % 179) - 89) *
           ::geometry::lat;
  }
  static ::geometry::Longitude CreateLongitude(const size_t salt) {
    return (static_cast<double>(((salt % 100) * 15 + salt / 3) % 359) - 179) *
           ::geometry::lon;
  }

  static ::geometry::Azimuth CreateDirection(const size_t salt) {
    return ::geometry::Azimuth::from_value(salt % 360);
  }
  /// Calling with same argument will provide same result
  static ::geometry::Position CreatePosition(const size_t salt) {
    return ::geometry::Position{CreateLatitude(salt), CreateLongitude(salt)};
  }

  static ::geometry::Viewport CreateViewport(const size_t salt_alpha,
                                             const size_t salt_beta) {
    return ::geometry::Viewport{CreatePosition(salt_alpha),
                                CreatePosition(salt_beta)};
  }
  static ::geometry::BoundingBox CreateBoundingBox(const size_t salt_alpha,
                                                   const size_t salt_beta) {
    return ::geometry::BoundingBox{CreatePosition(salt_alpha),
                                   CreatePosition(salt_beta)};
  }
  static ::geometry::CartesianPolygon CreateCartesianPolygon(
      const std::initializer_list<geometry::CartesianPosition>& points) {
    ::geometry::CartesianPolygon polygon;
    boost::geometry::assign_points(polygon, points);
    return polygon;
  }
};

}  // namespace geometry::test
