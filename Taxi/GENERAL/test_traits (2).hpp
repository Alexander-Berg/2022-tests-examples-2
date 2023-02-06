#pragma once

#include <channels/positions/lowlevel.hpp>
#include <channels/positions/traits.hpp>
#include <test/data_type_test_traits.hpp>
#include <types/data_type_traits.hpp>

namespace geobus::test {

/// Tratis for DriverPosition
template <>
struct DataTypeTestTraits<types::DriverPosition>
    : public types::DataTypeTraits<types::DriverPosition> {
  using Base = types::DataTypeTraits<types::DriverPosition>;
  using typename Base::Element;
  using typename Base::Elements;
  using typename Base::Generator;
  using typename Base::ParseInvalidStats;
  using typename Base::Payload;
  using typename Base::PositionsSpan;
  using typename Base::RandomGenerator;

  // Testing section
  template <typename Iterator>
  static void TestElementsAreEqual(
      Iterator start1, Iterator end1, Iterator start2, Iterator end2,
      test::ComparisonPrecision requestedPrecision =
          test::ComparisonPrecision::FullPrecision) {
    return test::PositionsTestPlugin::TestDriverPositionsArrayAreEqual(
        start1, end1, start2, end2, requestedPrecision);
  }
};

}  // namespace geobus::test
