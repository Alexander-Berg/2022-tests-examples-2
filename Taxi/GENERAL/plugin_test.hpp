#pragma once

#include <channels/edge_positions/edge_positions.hpp>
#include <geobus/channels/edge_positions/edge_positions.hpp>
#include <geobus/channels/edge_positions/edge_positions_generator.hpp>
#include <geobus/test/comparison_precision.hpp>

namespace geobus::test {

/// This plugin provides functions to create high-level and low-level
/// edge position structures.
/// All double/float members are created with integer values to allow comparison
/// with '=='
class EdgePositionsTestPlugin : public generators::EdgePositionsGenerator {
 public:
  /// Comparator for edge positions. In case you need to compare arrays
  /// of edge positions. ordering is by timestamp, then by driver_id
  static bool EdgePositionCompare(const types::DriverEdgePosition& first,
                                  const types::DriverEdgePosition& second);

  /// Tets that two DriverEdgePosition structures are equal. Double values are
  /// compared with precision we deemed sufficient.
  /// Non-double members are compared for equality.
  /// This method is only for unit-tests, obviously.
  /// @param requestedPrecision Take into account Flatbuffer limitation.
  static void TestDriverEdgePositionsAreClose(
      const types::DriverEdgePosition& first,
      const types::DriverEdgePosition& second,
      ComparisonPrecision requestedPrecision =
          ComparisonPrecision::FullPrecision);

  /// Compares to arrays of DriverEdgePosition using
  /// TestDriverEdgePositionsAreClose
  /// @param requestedPrecision Take into account Flatbuffer limitation.
  template <typename Iterator>
  static void TestDriverEdgePositionsArrayAreEqual(
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
#include "plugin_impl_test.hpp"
