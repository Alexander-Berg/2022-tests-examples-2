#include <geometry/cartesian_hexagon.hpp>

#include <userver/utest/utest.hpp>

namespace geometry {

TEST(CartesianHexagon, Basic) {
  auto hexagon = CartesianHexagon(hexagon_params::InscribedInEllipse{
      CartesianPosition{0 * lon, 1 * lat}, 2.0 * degree, 1.0 * degree});
  EXPECT_EQ(0 * lon, hexagon.Center().longitude);
  EXPECT_EQ(1 * lat, hexagon.Center().latitude);
  ASSERT_EQ(7, hexagon.Points().size());
  // Yes, the comparison must be exact. No epsilon. These must be
  // the same points.
  EXPECT_EQ(hexagon.Points()[0].longitude, hexagon.Points()[6].longitude);
  EXPECT_EQ(hexagon.Points()[0].latitude, hexagon.Points()[6].latitude);
}

TEST(CartesianHexagon, NonFinite) {
  EXPECT_ANY_THROW({
    CartesianHexagon(hexagon_params::InscribedInEllipse{
        CartesianPosition{std::nan("") * lon, std::nan("") * lat}, 2.0 * degree,
        1.0 * degree});
  });
}

TEST(CartesianHexagon, IsInside) {
  auto hexagon = CartesianHexagon(hexagon_params::InscribedInEllipse{
      CartesianPosition{0 * lon, 0 * lat}, 2.0 * degree, 1.0 * degree});

  EXPECT_TRUE(hexagon.IsInside(CartesianPosition{0 * lon, 0 * lat}));
  EXPECT_FALSE(hexagon.IsInside(CartesianPosition{0 * lon, 1. * lat}));
  EXPECT_TRUE(hexagon.IsInside(CartesianPosition{1.99 * lon, 0 * lat}));
  EXPECT_FALSE(hexagon.IsInside(CartesianPosition{2 * lon, 1 * lat}));
}

}  // namespace geometry
