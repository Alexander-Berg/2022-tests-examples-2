#pragma once

#include "plugin_test.hpp"

#include <tuple>

#include <userver/utest/utest.hpp>

namespace geobus::test {

inline bool EdgePositionsTestPlugin::EdgePositionCompare(
    const ::geobus::types::DriverEdgePosition& first,
    const ::geobus::types::DriverEdgePosition& second) {
  return std::tie(first.timestamp, first.driver_id) <
         std::tie(second.timestamp, second.driver_id);
}

inline void EdgePositionsTestPlugin::TestDriverEdgePositionsAreClose(
    const types::DriverEdgePosition& first,
    const types::DriverEdgePosition& second,
    [[maybe_unused]] ComparisonPrecision requestedPrecision) {
  ASSERT_EQ(first.driver_id, second.driver_id);
  ASSERT_EQ(first.timestamp, second.timestamp);
  ASSERT_EQ(first.possible_positions.size(), second.possible_positions.size());

  for (size_t i = 0; i < first.possible_positions.size(); ++i) {
    EXPECT_EQ(first.possible_positions[i], second.possible_positions[i]);
  }
}

/// Compares to arrays of DriverEdgePosition using
/// TestDriverEdgePositionsAreClose
/// @param requestedPrecision Take into account Flatbuffer limitation.
template <typename Iterator>
inline void EdgePositionsTestPlugin::TestDriverEdgePositionsArrayAreEqual(
    Iterator start1, Iterator end1, Iterator start2, Iterator end2,
    [[maybe_unused]] ComparisonPrecision requestedPrecision) {
  SCOPED_TRACE(__FUNCTION__);
  using namespace ::testing;
  for (size_t iteration = 0; start1 != end1 && start2 != end2;
       ++start1, ++start2, ++iteration) {
    SCOPED_TRACE(std::string("iterarion: ") + std::to_string(iteration));
    TestDriverEdgePositionsAreClose(*start1, *start2, requestedPrecision);
  }

  EXPECT_EQ((start1 == end1), (start2 == end2));
}
}  // namespace geobus::test
