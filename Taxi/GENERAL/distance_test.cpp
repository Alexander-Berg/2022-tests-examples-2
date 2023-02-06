#include <geometry/distance.hpp>

#include <gtest/gtest.h>
#include <boost/geometry/algorithms/distance.hpp>

#include <geometry/boost_geometry.hpp>
#include <geometry/wgs84.hpp>

namespace geometry {

class DistanceFixture : public testing::Test {};

TEST_F(DistanceFixture, GreateCircleDistanceTest) {
  using namespace ::geometry::literals;
  EXPECT_NEAR(316,
              GreatCircleDistance({55.785830_lat, 37.629652_lon},
                                  {55.786181_lat, 37.634646_lon})
                  .value(),
              50);

  EXPECT_NEAR(2390,
              GreatCircleDistance({55.784176_lat, 37.597160_lon},
                                  {55.786181_lat, 37.634646_lon})
                  .value(),
              50);
}

TEST_F(DistanceFixture, BoostGeometryHarvesine) {
  using namespace ::geometry::literals;
  {
    Position point_a{55.785830_lat, 37.629652_lon};
    Position point_b{55.786181_lat, 37.634646_lon};

    EXPECT_NEAR(316,
                boost::geometry::distance(
                    point_a, point_b,
                    boost::geometry::strategy::distance::haversine<double>(
                        kWgs84MajorSemiaxis)),
                50);
  }
  {
    Position point_a{55.784176_lat, 37.597160_lon};
    Position point_b{55.786181_lat, 37.634646_lon};

    EXPECT_NEAR(2390,
                boost::geometry::distance(
                    point_a, point_b,
                    boost::geometry::strategy::distance::haversine<double>(
                        kWgs84MajorSemiaxis)),
                50);
  }
}

TEST_F(DistanceFixture, SphericalProjectionDistanceTest) {
  using namespace ::geometry::literals;

  // ~ 0.1% diff is ok
  {
    Position point_a{55.785830_lat, 37.629652_lon};
    Position point_b{55.786181_lat, 37.634646_lon};

    EXPECT_NEAR(GreatCircleDistance(point_a, point_b).value(),
                SphericalProjectionDistance(point_a, point_b).value(), 0.4);
  }
  {
    Position point_a{55.784176_lat, 37.597160_lon};
    Position point_b{55.786181_lat, 37.634646_lon};

    EXPECT_NEAR(GreatCircleDistance(point_a, point_b).value(),
                SphericalProjectionDistance(point_a, point_b).value(), 2);
  }
}

}  // namespace geometry
