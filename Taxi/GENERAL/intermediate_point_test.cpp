#include <geometry/intermediate_point.hpp>

#include <gtest/gtest.h>

namespace geometry {

class IntermediatePointFixture : public testing::Test {};

TEST_F(IntermediatePointFixture, FractionIs0Test) {
  Position actual = IntermediatePoint(
      {Latitude::from_value(55.785830), Longitude::from_value(37.629652)},
      {Latitude::from_value(55.786181), Longitude::from_value(37.634646)}, 0.0);
  Position expected = {Latitude::from_value(55.785830),
                       Longitude::from_value(37.629652)};
  EXPECT_EQ(actual, expected);
}

TEST_F(IntermediatePointFixture, FractionIs1Test) {
  Position actual = IntermediatePoint(
      {Latitude::from_value(55.785830), Longitude::from_value(37.629652)},
      {Latitude::from_value(55.786181), Longitude::from_value(37.634646)}, 1.0);
  Position expected = {Latitude::from_value(55.786181),
                       Longitude::from_value(37.634646)};
  EXPECT_EQ(actual, expected);
}

TEST_F(IntermediatePointFixture, CommonTest) {
  Position actual = IntermediatePoint(
      {Latitude::from_value(55.785830), Longitude::from_value(37.629652)},
      {Latitude::from_value(55.786181), Longitude::from_value(37.634646)}, 0.3);
  Position expected = {Latitude::from_value(55.785935),
                       Longitude::from_value(37.631150)};
  EXPECT_NEAR(actual.latitude.value(), expected.latitude.value(), 1e-6);
  EXPECT_NEAR(actual.longitude.value(), expected.longitude.value(), 1e-6);
}

}  // namespace geometry
