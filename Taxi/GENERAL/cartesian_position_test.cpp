#include <geometry/cartesian_position.hpp>

#include <gtest/gtest.h>
#include <boost/geometry.hpp>

#include <geometry/viewport.hpp>

namespace geometry {

/// This test demostrates ability to use CartesianPoistion
/// and geometries, based on it, in boost::geometry::intersection algorithm.
///
/// Note, that this algorithm does not applicable for Position struct
/// because it registered in boost as geographic point
TEST(CartesianTest, Intesrsection) {
  // If one change point type to Position, this test won't be compiled
  // using Point = Position;
  using Point = CartesianPosition;
  using Polygon = boost::geometry::model::polygon<Point>;
  using Box = ViewportTpl<Point>;

  Polygon polygon;

  Point pos1(1.0 * lat, 1.0 * lon);
  Point pos2(1.0 * lat, 3.0 * lon);
  Point pos3(3.0 * lat, 1.0 * lon);

  boost::geometry::append(polygon, pos1);
  boost::geometry::append(polygon, pos2);
  boost::geometry::append(polygon, pos3);
  boost::geometry::append(polygon, pos1);

  // Prevent normalization because of boost box should have min/max _coreners
  Box box{Point{0.0 * lat, 0.0 * lon}, Point{2.0 * lat, 2.0 * lon}, false};

  std::vector<Polygon> intersection_out;
  boost::geometry::intersection(polygon, box, intersection_out);

  ASSERT_EQ(intersection_out.size(), 1);
}

}  // namespace geometry
