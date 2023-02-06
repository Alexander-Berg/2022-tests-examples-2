#pragma once

#include <channels/timelefts/lowlevel.hpp>
#include <channels/timelefts/traits.hpp>
#include <test/data_type_test_traits.hpp>
#include <types/data_type_traits.hpp>

namespace geobus::test {

/// Traits for
template <>
struct DataTypeTestTraits<types::Timelefts>
    : public types::DataTypeTraits<types::Timelefts> {
  using Base = types::DataTypeTraits<types::Timelefts>;
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

  static void TestTimeleftsAreEqual(
      const types::Timelefts& lhs, const types::Timelefts& rhs,
      [[maybe_unused]] test::ComparisonPrecision requestedPrecision =
          test::ComparisonPrecision::FullPrecision);
};

template <typename Iterator>
void DataTypeTestTraits<types::Timelefts>::TestElementsAreEqual(
    Iterator start1, Iterator end1, Iterator start2, Iterator end2,
    [[maybe_unused]] test::ComparisonPrecision requestedPrecision) {
  SCOPED_TRACE(__FUNCTION__);
  using namespace ::testing;
  for (size_t iteration = 0; start1 != end1 && start2 != end2;
       ++start1, ++start2, ++iteration) {
    SCOPED_TRACE(std::string("element: ") + std::to_string(iteration));
    TestTimeleftsAreEqual(*start1, *start2, requestedPrecision);
  }

  EXPECT_EQ((start1 == end1), (start2 == end2));
}

void DataTypeTestTraits<types::Timelefts>::TestTimeleftsAreEqual(
    const types::Timelefts& first, const types::Timelefts& second,
    [[maybe_unused]] test::ComparisonPrecision requestedPrecision) {
  ASSERT_EQ(first.contractor_id, second.contractor_id);
  ASSERT_EQ(first.timestamp, second.timestamp);
  ASSERT_EQ(first.tracking_type, second.tracking_type);
  ASSERT_EQ(first.route_id, second.route_id);
  ASSERT_EQ(first.adjusted_pos, second.adjusted_pos);
  ASSERT_EQ(first.timeleft_data.size(), second.timeleft_data.size());
  ASSERT_EQ(first.adjusted_segment_index, second.adjusted_segment_index);

  for (size_t i = 0; i < first.timeleft_data.size(); ++i) {
    EXPECT_EQ(first.timeleft_data[i], second.timeleft_data[i]);
  }
}

}  // namespace geobus::test
