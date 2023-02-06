#pragma once

#include <channels/universal_signals/traits.hpp>
#include <geobus/test/comparison_precision.hpp>
#include <test/data_type_test_traits.hpp>
#include <types/data_type_traits.hpp>
#include "lowlevel.hpp"

namespace geobus::test {

/// Traits for
template <>
struct DataTypeTestTraits<types::UniversalSignals>
    : public types::DataTypeTraits<types::UniversalSignals> {
  using Base = types::DataTypeTraits<types::UniversalSignals>;
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

  static void TestGeoSignalsAreEqual(
      const gpssignal::GpsSignal& lhs, const gpssignal::GpsSignal& rhs,
      [[maybe_unused]] test::ComparisonPrecision requestedPrecision =
          test::ComparisonPrecision::FullPrecision);

  static void TestPositionsOnEdgeAreEqual(
      const types::PositionOnEdge& lhs, const types::PositionOnEdge& rhs,
      [[maybe_unused]] test::ComparisonPrecision requestedPrecision =
          test::ComparisonPrecision::FullPrecision);

  static void TestUniversalSignalAreEqual(
      const types::UniversalSignal& lhs, const types::UniversalSignal& rhs,
      [[maybe_unused]] test::ComparisonPrecision requestedPrecision =
          test::ComparisonPrecision::FullPrecision);

  static void TestUniversalSignalsAreEqual(
      const types::UniversalSignals& lhs, const types::UniversalSignals& rhs,
      [[maybe_unused]] test::ComparisonPrecision requestedPrecision =
          test::ComparisonPrecision::FullPrecision);
};

template <typename Iterator>
void DataTypeTestTraits<types::UniversalSignals>::TestElementsAreEqual(
    Iterator start1, Iterator end1, Iterator start2, Iterator end2,
    [[maybe_unused]] test::ComparisonPrecision requestedPrecision) {
  SCOPED_TRACE(__FUNCTION__);
  using namespace ::testing;
  for (size_t iteration = 0; start1 != end1 && start2 != end2;
       ++start1, ++start2, ++iteration) {
    SCOPED_TRACE(std::string("element: ") + std::to_string(iteration));
    TestUniversalSignalsAreEqual(*start1, *start2, requestedPrecision);
  }

  EXPECT_EQ((start1 == end1), (start2 == end2));
}

void DataTypeTestTraits<types::UniversalSignals>::TestGeoSignalsAreEqual(
    const gpssignal::GpsSignal& lhs, const gpssignal::GpsSignal& rhs,
    test::ComparisonPrecision requestedPrecision) {
  if (requestedPrecision == test::ComparisonPrecision::FullPrecision) {
    EXPECT_EQ(lhs, rhs);
  } else if (requestedPrecision == test::ComparisonPrecision::FbsPrecision) {
    EXPECT_EQ(lhs.timestamp, rhs.timestamp);
    EXPECT_EQ(lhs.speed.has_value(), rhs.speed.has_value());
    if (lhs.speed && rhs.speed) {
      EXPECT_NEAR(lhs.speed->value(), rhs.speed->value(), 0.001);
    }
    EXPECT_EQ(lhs.direction.has_value(), rhs.direction.has_value());
    if (lhs.direction && rhs.direction) {
      EXPECT_EQ(static_cast<int>(lhs.direction->value()),
                static_cast<int>(rhs.direction->value()));
    }
    EXPECT_EQ(lhs.accuracy.has_value(), rhs.accuracy.has_value());
    if (lhs.accuracy && rhs.accuracy) {
      EXPECT_NEAR(lhs.accuracy->value(), rhs.accuracy->value(), 0.001);
    }
    EXPECT_EQ(lhs.altitude.has_value(), rhs.altitude.has_value());
    if (lhs.altitude && rhs.altitude) {
      EXPECT_EQ(static_cast<int>(lhs.altitude->value()),
                static_cast<int>(rhs.altitude->value()));
    }
    EXPECT_EQ(static_cast<geometry::Position>(lhs),
              static_cast<geometry::Position>(rhs));
  }
}

void DataTypeTestTraits<types::UniversalSignals>::TestPositionsOnEdgeAreEqual(
    const types::PositionOnEdge& lhs, const types::PositionOnEdge& rhs,
    test::ComparisonPrecision requestedPrecision) {
  if (requestedPrecision == test::ComparisonPrecision::FullPrecision) {
    EXPECT_EQ(lhs, rhs);
  } else if (requestedPrecision == test::ComparisonPrecision::FbsPrecision) {
    EXPECT_EQ(lhs.persistent_edge_id, rhs.persistent_edge_id);
    EXPECT_NEAR(lhs.edge_displacement, rhs.edge_displacement, 1.0 / 65535.0);
  }
}

void DataTypeTestTraits<types::UniversalSignals>::TestUniversalSignalAreEqual(
    const types::UniversalSignal& lhs, const types::UniversalSignal& rhs,
    test::ComparisonPrecision requestedPrecision) {
  if (requestedPrecision == test::ComparisonPrecision::FullPrecision) {
    EXPECT_EQ(lhs, rhs);
  } else if (requestedPrecision == test::ComparisonPrecision::FbsPrecision) {
    TestGeoSignalsAreEqual(lhs.geo_signal, rhs.geo_signal, requestedPrecision);
    EXPECT_EQ(lhs.position_on_edge.has_value(),
              rhs.position_on_edge.has_value());
    if (lhs.position_on_edge && rhs.position_on_edge) {
      TestPositionsOnEdgeAreEqual(*lhs.position_on_edge, *rhs.position_on_edge,
                                  requestedPrecision);
    }
    EXPECT_EQ(lhs.prediction_shift, rhs.prediction_shift);
    EXPECT_EQ(lhs.log_likelihood, rhs.log_likelihood);
    EXPECT_NEAR(lhs.probability, rhs.probability, 1.0 / 255.0);
  }
}

void DataTypeTestTraits<types::UniversalSignals>::TestUniversalSignalsAreEqual(
    const types::UniversalSignals& first, const types::UniversalSignals& second,
    [[maybe_unused]] test::ComparisonPrecision requestedPrecision) {
  EXPECT_EQ(first.contractor_id, second.contractor_id);
  EXPECT_EQ(first.client_timestamp, second.client_timestamp);
  EXPECT_EQ(first.source, second.source);
  ASSERT_EQ(first.signals.size(), second.signals.size());
  for (size_t i = 0; i < first.signals.size(); ++i) {
    TestUniversalSignalAreEqual(first.signals[i], second.signals[i],
                                requestedPrecision);
  }

  ASSERT_EQ(first.sensors.size(), second.sensors.size());
  for (size_t i = 0; i < first.sensors.size(); ++i) {
    EXPECT_EQ(first.sensors[i].first, second.sensors[i].first);
    EXPECT_EQ(first.sensors[i].second, second.sensors[i].second);
  }
}

}  // namespace geobus::test
