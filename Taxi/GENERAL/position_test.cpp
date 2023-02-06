#include <geometry/position.hpp>

#include <gtest/gtest.h>

#include <geometry/test/geometry_plugin_test.hpp>

namespace geometry {

using geometry::test::GeometryTestPlugin;

class PositionFixture : public ::testing::Test {};

TEST_F(PositionFixture, Equality) {
  EXPECT_EQ((Position{10.0 * lat, 20.0 * lon}),
            (Position{10.0 * lat, 20.0 * lon}));
  EXPECT_NE((Position{10.0 * lat, 20.0 * lon}),
            (Position{10.0 * lat, 21.0 * lon}));
}

TEST_F(PositionFixture, CreateAnyOrder) {
  {
    Position pos(5.0 * lat, 7.0 * lon);

    EXPECT_EQ(7.0 * lon, pos.longitude);
    EXPECT_EQ(5.0 * lat, pos.latitude);
  }
  {
    Position pos(7.0 * lon, 5.0 * lat);

    EXPECT_EQ(7.0 * lon, pos.longitude);
    EXPECT_EQ(5.0 * lat, pos.latitude);
  }
}

TEST_F(PositionFixture, Normalize) {
  {
    Position pos(7.0 * lon, 5.0 * lat);
    pos.Normalize();
    GeometryTestPlugin::TestPositionsAreClose(pos, {7.0 * lon, 5.0 * lat});
  }
  {
    Position pos(185.0 * lon, 91.0 * lat);
    pos.Normalize();
    GeometryTestPlugin::TestPositionsAreClose(pos, {-175.0 * lon, 90.0 * lat});
  }
  {
    Position pos(-545.0 * lon, -91.0 * lat);
    pos.Normalize();
    GeometryTestPlugin::TestPositionsAreClose(pos, {175.0 * lon, -90.0 * lat});
  }
  {
    Position pos(std::numeric_limits<double>::infinity() * lon,
                 std::numeric_limits<double>::infinity() * lat);
    pos.Normalize();
    ASSERT_TRUE(!pos.IsFinite());
  }
}

TEST_F(PositionFixture, Delta) {
  using namespace geometry::literals;
  {
    LongitudeDelta d1{0.1};
    LatitudeDelta d2{0.2};
    PositionDelta dl1{d1, d2};
    PositionDelta dl2{d2, d1};
    EXPECT_EQ(dl1, dl2);
  }
  // Test that deltas can be created conviniently
  { PositionDelta dl{LongitudeDelta{0.1}, LatitudeDelta{0.2}}; }

  {
    // summation
    PositionDelta dl{LongitudeDelta{1.0}, LatitudeDelta{2.0}};
    Position pos{9.0_lon, 8.0_lat};
    EXPECT_EQ((Position{10.0_lon, 10.0_lat}), pos + dl);
  }

  {
    // substraction
    PositionDelta dl{LongitudeDelta{-1.0}, LatitudeDelta{-2.0}};
    Position pos{9.0_lon, 8.0_lat};
    EXPECT_EQ((Position{10.0_lon, 10.0_lat}), pos - dl);
  }
}

TEST_F(PositionFixture, DeltaEquality) {
  EXPECT_EQ((PositionDelta{10.0 * dlat, 20.0 * dlon}),
            (PositionDelta{10.0 * dlat, 20.0 * dlon}));
  EXPECT_NE((PositionDelta{10.0 * dlat, 20.0 * dlon}),
            (PositionDelta{10.0 * dlat, 21.0 * dlon}));
}

}  // namespace geometry
