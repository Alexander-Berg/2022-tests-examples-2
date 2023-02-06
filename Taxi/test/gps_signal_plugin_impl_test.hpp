#pragma once

#include <gtest/gtest.h>

namespace geobus::test {

inline void GpsSignalTestPlugin::TestGpsSignalsAreClose(
    const ::geobus::types::GpsSignalExtended& first,
    const ::geobus::types::GpsSignalExtended& second,
    ComparisonPrecision requestedPrecision) {
  SCOPED_TRACE(__FUNCTION__);
  EXPECT_EQ(first.source, second.source);
  if (requestedPrecision == ComparisonPrecision::FullPrecision) {
    ::gpssignal::test::GpsSignalTestPlugin::TestGpsSignalsAreClose(first,
                                                                   second);
  } else {
    /// Copy of same method from GpsTestPlugin, but with adjusted speed
    /// threshold
    TestLatitudesAreClose(first.latitude, second.latitude);
    TestLongitudesAreClose(first.longitude, second.longitude);
    EXPECT_EQ(static_cast<bool>(first.speed), static_cast<bool>(second.speed));
    // We use EXPECT, not ASSERT, so have to check both values
    if (first.speed && second.speed) {
      EXPECT_NEAR(first.speed->value(), second.speed->value(),
                  kFbsSpeedMpsPrecision);
    }
    EXPECT_EQ(static_cast<bool>(first.direction),
              static_cast<bool>(second.direction));
    if (first.direction && second.direction) {
      TestDirectionsAreClose(*first.direction, *second.direction);
    }
    EXPECT_EQ(static_cast<bool>(first.accuracy),
              static_cast<bool>(second.accuracy));
    // We use EXPECT, not ASSERT, so have to check both values
    if (first.accuracy && second.accuracy) {
      EXPECT_EQ(*first.accuracy, *second.accuracy);
    }
    EXPECT_EQ(first.timestamp, second.timestamp);
  }
}

}  // namespace geobus::test
