#pragma once

#include <geometry/position.hpp>
#include <geometry/viewport.hpp>

#include <geometry/test/geometry_plugin_test.hpp>
#include <gpssignal/test/gpssignal_generator.hpp>

#include <gtest/gtest.h>

namespace gpssignal::test {

/// This plugin provides functions for creating and comparing gps signals  and
/// related classes.
/// Passing same salt will result in same value
/// All double/float members are created with integer values to allow comparison
/// with '=='
class GpsSignalTestPlugin : public ::geometry::test::GeometryTestPlugin,
                            public GpsSignalGenerator {
 public:
  static const constexpr double kSpeedCloseThreshold = 0.01;     // m/s
  static const constexpr double kDirectionCloseThreshold = 0.5;  // degree

  /// Tests that gps signals are close enough for testing purposes
  static void TestGpsSignalsAreClose(const ::gpssignal::GpsSignal& first,
                                     const ::gpssignal::GpsSignal& second);

  /// Tests that speeds are close enough for testing purposes
  static void TestSpeedsAreClose(const ::gpssignal::Speed speed1,
                                 const ::gpssignal::Speed speed2) {
    EXPECT_NEAR(speed1.value(), speed2.value(), kSpeedCloseThreshold);
  }

  void PluginSetUp() {}
  void PluginTearDown() {}
  static void PluginSetUpTestSuite() {}
  static void PluginTearDownTestSuite() {}
};

inline void GpsSignalTestPlugin::TestGpsSignalsAreClose(
    const ::gpssignal::GpsSignal& first, const ::gpssignal::GpsSignal& second) {
  SCOPED_TRACE(__FUNCTION__);
  TestPositionsAreClose(first, second);
  EXPECT_EQ(static_cast<bool>(first.speed), static_cast<bool>(second.speed));
  // We use EXPECT, not ASSERT, so have to check both values
  if (first.speed && second.speed) {
    TestSpeedsAreClose(*first.speed, *second.speed);
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

}  // namespace gpssignal::test
