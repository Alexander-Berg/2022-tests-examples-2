#pragma once

#include <channels/edge_positions/edge_positions.hpp>
#include <channels/edge_positions/edge_positions_traits.hpp>
#include <geobus/channels/edge_positions/plugin_test.hpp>
#include <geobus/test/comparison_precision.hpp>
#include <test/data_type_test_traits.hpp>
#include <types/data_type_traits.hpp>

namespace geobus::test {

/// Tratis for DriverEdgePosition
template <>
struct DataTypeTestTraits<types::DriverEdgePosition>
    : public types::DataTypeTraits<types::DriverEdgePosition> {
  using Base = types::DataTypeTraits<types::DriverEdgePosition>;
  using typename Base::EdgePositionsSpan;
  using typename Base::Element;
  using typename Base::Elements;
  using typename Base::Generator;
  using typename Base::ParseInvalidStats;
  using typename Base::Payload;
  using typename Base::RandomGenerator;

  // Testing section
  template <typename Iterator>
  static void TestElementsAreEqual(
      Iterator start1, Iterator end1, Iterator start2, Iterator end2,
      test::ComparisonPrecision requestedPrecision =
          test::ComparisonPrecision::FullPrecision) {
    return test::EdgePositionsTestPlugin::TestDriverEdgePositionsArrayAreEqual(
        start1, end1, start2, end2, requestedPrecision);
  }
};

}  // namespace geobus::test
