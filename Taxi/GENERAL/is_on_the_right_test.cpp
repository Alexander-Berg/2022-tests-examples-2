#include <geometry/is_on_the_right.hpp>

#include <gtest/gtest.h>

namespace geometry {

class IsOnTheRightFixture : public ::testing::Test {};

TEST_F(IsOnTheRightFixture, meridian_aligned) {
  Position start{37 * lon, 55 * lat};
  Position end{37 * lon, 56 * lat};

  Position right_point{37.5 * lon, 55.5 * lat};
  Position left_point{36.5 * lon, 55.5 * lat};
  EXPECT_TRUE(IsOnTheRight(Line{start, end}, right_point));
  EXPECT_FALSE(IsOnTheRight(Line{start, end}, left_point));
}

TEST_F(IsOnTheRightFixture, parallel_aligned) {
  Position start{36 * lon, 55 * lat};
  Position end{37 * lon, 55 * lat};

  Position top_point{36.5 * lon, 55.5 * lat};
  Position bottom_point{36.5 * lon, 54.5 * lat};
  EXPECT_FALSE(IsOnTheRight(Line{start, end}, top_point));
  EXPECT_TRUE(IsOnTheRight(Line{start, end}, bottom_point));
}

TEST_F(IsOnTheRightFixture, precision) {
  {
    Position start{37.4759047 * lon, 55.7178388 * lat};
    Position end{37.476334 * lon, 55.718281 * lat};

    Position left_point{37.475904 * lon, 55.717966 * lat};
    Position right_point{37.476092 * lon, 55.717923 * lat};
    EXPECT_TRUE(IsOnTheRight(Line{start, end}, right_point));
    EXPECT_FALSE(IsOnTheRight(Line{start, end}, left_point));
  }

  {
    // oposite edge direction
    Position end{37.4759047 * lon, 55.7178388 * lat};
    Position start{37.476334 * lon, 55.718281 * lat};

    Position left_point{37.475904 * lon, 55.717966 * lat};
    Position right_point{37.476092 * lon, 55.717923 * lat};
    EXPECT_FALSE(IsOnTheRight(Line{start, end}, right_point));
    EXPECT_TRUE(IsOnTheRight(Line{start, end}, left_point));
  }
}

TEST_F(IsOnTheRightFixture, exception) {
  Position non_finite_pos;
  non_finite_pos.SetLongitudeFromDouble(std::nan(""));
  non_finite_pos.SetLatitudeFromDouble(std::nan(""));

  Line non_finite_line{non_finite_pos, non_finite_pos};

  ASSERT_ANY_THROW(IsOnTheRight(non_finite_line, Position{0 * lat, 5 * lon}));
  ASSERT_ANY_THROW(
      IsOnTheRight(Line{Position{0 * lat, 5 * lon}, Position{1 * lat, 7 * lon}},
                   non_finite_pos));
}

}  // namespace geometry
