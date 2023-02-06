#pragma once

#include <channels/signal_v2/lowlevel.hpp>
#include <channels/signal_v2/traits.hpp>
#include <geobus/test/comparison_precision.hpp>
#include <test/data_type_test_traits.hpp>
#include <types/data_type_traits.hpp>

namespace geobus::test {

/// Traits for SignalV2
template <>
struct DataTypeTestTraits<types::SignalV2>
    : public types::DataTypeTraits<types::SignalV2> {
  using Base = types::DataTypeTraits<types::SignalV2>;
  using typename Base::Element;
  using typename Base::Elements;
  using typename Base::Generator;
  using typename Base::ParseInvalidStats;
  using typename Base::Payload;
  using typename Base::RandomGenerator;
  using typename Base::Span;

  template <typename Iterator>
  static void TestElementsAreEqual(
      Iterator start1, Iterator end1, Iterator start2, Iterator end2,
      [[maybe_unused]] test::ComparisonPrecision requestedPrecision =
          test::ComparisonPrecision::FullPrecision);
};

template <typename Iterator>
void DataTypeTestTraits<types::SignalV2>::TestElementsAreEqual(
    Iterator start1, Iterator end1, Iterator start2, Iterator end2,
    [[maybe_unused]] test::ComparisonPrecision requestedPrecision) {
  for (size_t iteration = 0; start1 != end1 && start2 != end2;
       ++start1, ++start2, ++iteration) {
    const types::SignalV2& first = *start1;
    const types::SignalV2& second = *start2;

    ASSERT_EQ(first.driver_id, second.driver_id);
    ASSERT_EQ(first.position, second.position);
    ASSERT_EQ(first.unix_time, second.unix_time);
    ASSERT_EQ(first.altitude, second.altitude);
    ASSERT_EQ(first.direction, second.direction);
    ASSERT_EQ(first.speed, second.speed);
    ASSERT_EQ(first.accuracy, second.accuracy);
  }

  EXPECT_EQ((start1 == end1), (start2 == end2));
}
}  // namespace geobus::test
