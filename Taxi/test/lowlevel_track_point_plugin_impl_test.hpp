#pragma once

#include <gtest/gtest.h>

namespace geobus::test {

inline void LowlevelTrackPointTestPlugin::TestTrackPointsAreClose(
    const lowlevel::TrackPoint& first, const lowlevel::TrackPoint& second,
    ComparisonPrecision requestedPrecision) {
  SCOPED_TRACE(__FUNCTION__);
  EXPECT_EQ(first.source, second.source);
  TestLatitudesAreClose(first.latitude * ::geometry::lat,
                        second.latitude * ::geometry::lat);
  TestLongitudesAreClose(first.longitude * ::geometry::lon,
                         second.longitude * ::geometry::lon);
  TestDirectionsAreClose(::geometry::Azimuth::from_value(first.direction),
                         ::geometry::Azimuth::from_value(second.direction));

  const double speedThreshold =
      (requestedPrecision == ComparisonPrecision::FbsPrecision)
          ? kFbsSpeedKmphPrecision
          : kSpeedKmphPrecision;
  EXPECT_NEAR(first.speed_kmph, second.speed_kmph, speedThreshold);
  EXPECT_EQ(first.timestamp, second.timestamp);
  EXPECT_EQ(first.accuracy, second.accuracy);
}

}  // namespace geobus::test
