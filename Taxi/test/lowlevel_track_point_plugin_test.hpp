#pragma once

#include <generators/lowlevel_gps_signal_generator.hpp>
#include <geobus/channels/positions/track_point.hpp>
#include <geobus/generators/gpssignal_generator.hpp>
#include <geobus/test/comparison_precision.hpp>
#include <geobus/test/driver_id_plugin_test.hpp>
#include <geobus/types/gps_signal_extended.hpp>
#include <gpssignal/test/gpssignal_plugin_test.hpp>

#include <gtest/gtest.h>

namespace geobus::test {

/// This plugin provides functions to create high-level and low-level
/// gps signals.
/// All double/float members are created with integer values to allow comparison
/// with '=='
struct LowlevelTrackPointTestPlugin
    : public ::gpssignal::test::GpsSignalTestPlugin,
      public geobus::generators::GpsSignalGenerator,
      public geobus::generators::LowlevelGpsSignalGenerator {
  /// Tets that two TrackPoint structures are equal. Double values are
  /// compared with precision we deemed sufficient.
  /// Non-double members are compared for equality.
  /// This method is only for unit-tests, obviously.
  /// Testing is done internaly with EXPECT_XXX macroses.
  static void TestTrackPointsAreClose(const lowlevel::TrackPoint& first,
                                      const lowlevel::TrackPoint& second,
                                      ComparisonPrecision requestedPrecision =
                                          ComparisonPrecision::FullPrecision);

  void PluginSetUp() {}
  void PluginTearDown() {}
  static void PluginSetUpTestSuite() {}
  static void PluginTearDownTestSuite() {}
};

}  // namespace geobus::test

/// Due to limitation of libraries handling, we have to provide implementation
/// as include file
#include "lowlevel_track_point_plugin_impl_test.hpp"
