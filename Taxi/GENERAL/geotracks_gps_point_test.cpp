#include "geotracks-protocol/geotracks_gps_point.hpp"

#include <gtest/gtest.h>

TEST(geotracks_protocol, FbsSerialize) {
  geotracks_protocol::GpsPoint orig(
      42, ::gpssignal::Azimuth::from_value(42),
      ::geometry::Position(37 * ::gpssignal::lon, 55 * ::gpssignal::lat),
      ::geometry::Position(137 * ::gpssignal::lon, 155 * ::gpssignal::lat),
      16 * ::gpssignal::km_per_hour,
      geotracks_protocol::DriverServerStatus::FREE, 15000000,
      ::gpssignal::Distance::from_value(49.5), 1);
  const auto serialized = geotracks_protocol::SerializeGeotracksGpsPoint(orig);
  const auto deserilized =
      geotracks_protocol::DeserializeGeotracksGpsPoint(serialized);

  EXPECT_EQ(orig, deserilized);
}
