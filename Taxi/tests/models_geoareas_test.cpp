#include <gtest/gtest.h>

#include <boost/geometry.hpp>
#include <models/geoarea.hpp>

TEST(ModelGeoarea, One) {
  Geoarea::polygon_t polygon;
  boost::geometry::append(polygon, Geoarea::point_t(77.0084, 43.3474));
  boost::geometry::append(polygon, Geoarea::point_t(77.0118, 43.3487));
  boost::geometry::append(polygon, Geoarea::point_t(77.0132, 43.3457));
  boost::geometry::append(polygon, Geoarea::point_t(77.0099, 43.3451));
  boost::geometry::append(polygon, Geoarea::point_t(77.0084, 43.3474));
  boost::geometry::append(polygon, Geoarea::point_t(77.0084, 43.3474));
  auto geoarea = Geoarea("5a3e5b1a934248ab8e512abf9aa54f57", "", 0, polygon,
                         0.0, Geoarea::Type::Airport);
  EXPECT_TRUE(geoarea.contains_point_fast({77.010472, 43.345995}));
}
