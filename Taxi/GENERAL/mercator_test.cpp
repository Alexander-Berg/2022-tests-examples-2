#include <geometry/mercator.hpp>

#include <gtest/gtest.h>

TEST(MercatorTest, Zero) {
  using namespace geometry;
  const auto res = ConvertToMercator(0 * lon, 0 * lat);
  EXPECT_NEAR(res.x.value(), 0.0, 0.0001);
  EXPECT_NEAR(res.y.value(), 0.0, 0.0001);
}
