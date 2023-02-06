#include <gtest/gtest.h>
#include <geometry-fbs/geometry-fbs.hpp>
#include <geometry/test/geometry_plugin_test.hpp>

TEST(geometry_fbs, base) {
  ::geometry::Position original(37.37 * ::geometry::lon,
                                55.55 * ::geometry::lat);
  auto fbs = ::geometry_fbs::ToFlatbuffers(original);
  auto converted = ::geometry_fbs::ToPosition(fbs);

  ::geometry::test::GeometryTestPlugin::TestPositionsAreClose(original,
                                                              converted);
}

TEST(geometry_fbs, nan) {
  ::geometry::Position original(
      std::numeric_limits<double>::quiet_NaN() * ::geometry::lon,
      55.55 * ::geometry::lat);
  auto fbs = ::geometry_fbs::ToFlatbuffers(original);
  auto converted = ::geometry_fbs::ToPosition(fbs);

  EXPECT_FALSE(converted.IsFinite());
}

TEST(geometry_fbs, array) {
  using ::geometry::lat;
  using ::geometry::lon;
  using namespace ::geometry::literals;

  std::vector reference{geometry::Position(10.0_lon, 15.0_lat),
                        geometry::Position(20.0_lon, 30.0_lat)};

  auto fbs = ::geometry_fbs::ToFlatbuffers(reference);
  EXPECT_EQ(reference.size(), fbs.size());
}
