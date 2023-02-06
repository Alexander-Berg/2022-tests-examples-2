#pragma once

#include <channels/positions/lowlevel.hpp>
#include <geobus/channels/positions/positions_generator.hpp>
#include <geobus/channels/positions/track_point.hpp>
#include <geobus/test/comparison_precision.hpp>
#include <geobus/test/driver_id_plugin_test.hpp>
#include <geobus/test/gps_signal_plugin_test.hpp>
#include <geobus/test/print_to.hpp>
#include <geobus/types/driver_position.hpp>
#include <test/lowlevel_track_point_plugin_test.hpp>

namespace geobus::test {

/// This plugin provides functions to create high-level and low-level
/// edge position structures.
/// All double/float members are created with integer values to allow comparison
/// with '=='
class LowlevelPositionsTestPlugin : public DriverIdTestPlugin,
                                    public GpsSignalTestPlugin,
                                    public LowlevelTrackPointTestPlugin,
                                    public generators::PositionsGenerator {
 public:
  /// Tets that two DriverPositionInfo structures are equal. Double values are
  /// compared with precision we deemed sufficient.
  /// Non-double members are compared for equality.
  /// This method is only for unit-tests, obviously.
  /// @param requestedPrecision Take into account Flatbuffer limitation.
  static void TestDriverPositionsAreClose(
      const lowlevel::DriverPositionInfo& first,
      const lowlevel::DriverPositionInfo& second,
      ComparisonPrecision requestedPrecision =
          ComparisonPrecision::FullPrecision);

  /// Compares to arrays of DriverPosition/DriverPositionInfo using
  /// TestDriverPositionsAreClose
  /// @param requestedPrecision Take into account Flatbuffer limitation.
  template <typename Iterator>
  static void TestDriverPositionsArrayAreEqual(
      Iterator start1, Iterator end1, Iterator start2, Iterator end2,
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
#include "lowlevel_positions_plugin_impl_test.hpp"
