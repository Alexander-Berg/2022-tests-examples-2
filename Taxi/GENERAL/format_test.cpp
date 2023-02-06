#include <geometry/format.hpp>

#include <gtest/gtest.h>

namespace geometry {

TEST(Format, Position) {
  Position p1{10.0 * lat, 20.0 * lon};
  Position p2{10.0 * lat, 21.0 * lon};

  EXPECT_EQ(fmt::format("{}", p1), "(20; 10)");
  EXPECT_NE(fmt::format("{}", p1), fmt::format("{}", p2));
}

}  // namespace geometry
