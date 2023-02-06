
#include <eventus/polygons/geometry.hpp>

#include <userver/utest/utest.hpp>

// fix like in https://st.yandex-team.ru/TAXICOMMON-1749
#ifdef PESRQUEUE_WRAPPER_ARC_BUILD
#include <taxi/libpq-wrapper/lib/include/logger.h>
#include <taxi/libpq-wrapper/lib/include/utils.h>
#else
#include <yandex/taxi/persqueue-wrapper/logger.h>  // Y_IGNORE
#include <yandex/taxi/persqueue-wrapper/utils.h>   // Y_IGNORE
#endif

template <>
void NTaxi::NLibPqWrapper::THolder<NTaxi::NLibPqWrapper::TLogger>::Delete() {
  delete ptr;
}
///////////////////////////////////////////////////////

namespace eventus::polygons::geometry {

namespace {

struct TestPoint {
  ::std::vector<double> coordinates{};
};

struct TestPolygon {
  ::std::vector<TestPoint> points{};
};

}  // namespace

UTEST(Geometry, points_from_lavka_config) {
  // {.points=[]{ { .coordinates=[]{0.0, 0.0} }, ... } }
  TestPolygon polygon_{{
      {{0.0, 20.0}},
      {{21.0, 21.0}},
      {{20.0, 0.0}},
      {{0.0, 0.0}},
  }};
  std::vector<Polygon> polygons{{"1", polygon_}};

  Point within = Point::FromLonLat(10.0, 15.0),
        within2 = Point::FromLonLat(20.0, 20.0),
        without = Point::FromLonLat(30.0, 15.0);

  ASSERT_TRUE(polygons[0].IsValid());
  ASSERT_TRUE(polygons[0].Contains(within));
  ASSERT_TRUE(polygons[0].Contains(within2));
  ASSERT_FALSE(polygons[0].Contains(without));

  ASSERT_TRUE(PointInAnyPolygon(within, polygons));
  ASSERT_FALSE(PointInAnyPolygon(without, polygons));
}

UTEST(Geometry, points_from_vector) {
  Polygon polygon_cw("cw", std::vector<Point>{
                               Point::FromLonLat(0.0, 20.0),
                               Point::FromLonLat(21.0, 21.0),
                               Point::FromLonLat(20.0, 0.0),
                               Point::FromLonLat(0.0, 0.0),
                           });
  Polygon polygon_ccw("ccw", std::vector<Point>{
                                 Point::FromLonLat(0.0, 0.0),
                                 Point::FromLonLat(20.0, 0.0),
                                 Point::FromLonLat(21.0, 21.0),
                                 Point::FromLonLat(0.0, 20.0),
                             });
  std::vector<Polygon> polygons = {polygon_cw, polygon_ccw};

  Point within = Point::FromLonLat(10.0, 15.0),
        within2 = Point::FromLonLat(20.0, 20.0),
        without = Point::FromLonLat(30.0, 15.0);

  ASSERT_TRUE(polygons[0].IsValid());
  ASSERT_TRUE(polygons[0].Contains(within));
  ASSERT_TRUE(polygons[0].Contains(within2));
  ASSERT_FALSE(polygons[0].Contains(without));

  ASSERT_TRUE(polygons[1].IsValid());
  ASSERT_TRUE(polygons[1].Contains(within));
  ASSERT_TRUE(polygons[1].Contains(within2));
  ASSERT_FALSE(polygons[1].Contains(without));

  ASSERT_TRUE(PointInAnyPolygon(within, polygons));
  ASSERT_FALSE(PointInAnyPolygon(without, polygons));
}

TEST(Geometry, point_in_polygon_for_rule_test_support) {
  Polygon polygon("pt", std::vector<Point>{Point::FromLonLat(0.0, 10.0),
                                           Point::FromLonLat(10.0, 5.0),
                                           Point::FromLonLat(0.0, 0.0)});
  ASSERT_TRUE(polygon.IsValid());
  ASSERT_TRUE(polygon.Contains(Point::FromLonLat(5.0, 5.0)));
}

}  // namespace eventus::polygons::geometry
