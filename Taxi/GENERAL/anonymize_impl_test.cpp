#include <gtest/gtest.h>

#include <geometry/position_as_array.hpp>
#include <geometry/position_as_object.hpp>

#include <utils/anonymize_impl.hpp>

TEST(TestMakeLowAccuracy, TestDouble) {
  double test_value = 3.1415926536;
  const double expected_value = 3.141;
  EXPECT_NE(test_value, expected_value);
  test_value = utils::MakeLowAccuracy(test_value);
  EXPECT_DOUBLE_EQ(test_value, expected_value);
}

TEST(TestMakeLowAccuracy, TestWaypoint) {
  geometry::PositionAsObject test_value{59.95016 * geometry::lat,
                                        30.31785 * geometry::lon};
  const geometry::PositionAsObject expected_value{59.950 * geometry::lat,
                                                  30.317 * geometry::lon};
  EXPECT_NE(test_value, expected_value);
  test_value = utils::MakeLowAccuracy(std::move(test_value));
  EXPECT_EQ(test_value, expected_value);
}

TEST(TestMakeLowAccuracy, TestWaypointsArray) {
  std::vector test_value{
      geometry::Position{59.95016 * geometry::lat, 30.31785 * geometry::lon},
      geometry::Position{55.75585 * geometry::lat, 37.61776 * geometry::lon},
  };
  const std::vector expected_value{
      geometry::Position{59.950 * geometry::lat, 30.317 * geometry::lon},
      geometry::Position{55.755 * geometry::lat, 37.617 * geometry::lon},
  };
  EXPECT_NE(test_value, expected_value);
  test_value = utils::MakeLowAccuracy(std::move(test_value));
  EXPECT_EQ(test_value, expected_value);
}
