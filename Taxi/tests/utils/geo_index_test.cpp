#include <userver/utest/utest.hpp>

#include <geometry/distance.hpp>
#include <geometry/units.hpp>
#include <iostream>

#include <geo/utils/geo_index.hpp>

namespace {

namespace gm = ::geometry;

using GeoIndex = ::maas::geo::GeoIndex;

std::vector<gm::Position> CreateGrid(const gm::Position& center,
                                     const gm::Distance& cell_size,
                                     int n_cells) {
  auto lon_deg_len = gm::LongitudeDegreeLength(center.latitude);
  auto lat_deg_len = gm::LatitudeDegreeLength(center.latitude);
  std::vector<gm::Position> grid;
  for (int ci = -n_cells; ci <= n_cells; ++ci) {
    for (int cj = -n_cells; cj <= n_cells; ++cj) {
      auto delta = ::geometry::PositionDelta(
          (ci * 1.0 * cell_size / lon_deg_len) * gm::dlon,
          (cj * 1.0 * cell_size / lat_deg_len) * gm::dlat);
      grid.push_back(center + delta);
    }
  }
  return grid;
}

}  // namespace

TEST(TestGeoIndex, TestHasPointsInCircle) {
  auto center = gm::Position(37.5 * gm::lon, 55.5 * gm::lat);
  // create grid with center in [37.5, 55.5]
  // grid size is 250x250 meters with cell size 5x5 meters
  auto cell_size = 5 * gm::meters;
  auto n_cells = 25;
  std::vector<gm::Position> grid = CreateGrid(center, cell_size, n_cells);

  ASSERT_EQ((n_cells * 2 + 1) * (n_cells * 2 + 1), grid.size());

  auto radius = 100 * gm::meters;
  std::vector<gm::Position> points_in_circle, points_out_of_circle;
  for (const auto& point : grid) {
    if (gm::SphericalProjectionDistance(center, point) <= radius) {
      points_in_circle.push_back(point);
    } else {
      points_out_of_circle.push_back(point);
    }
  }

  double circle_area = M_PI * pow(radius.value(), 2);
  double grid_area = pow(cell_size.value() * n_cells * 2, 2);
  ASSERT_NEAR(points_in_circle.size() * 1.0 / grid.size(),
              circle_area / grid_area, (circle_area / grid_area) * 0.05);

  GeoIndex geo_index_grid{grid};
  for (const auto& point : grid) {
    ASSERT_TRUE(geo_index_grid.HasPointsInCircle(point, 1 * gm::meters));
    ASSERT_TRUE(geo_index_grid.HasPointsInCircle(point, 10 * gm::meters));
    ASSERT_TRUE(geo_index_grid.HasPointsInCircle(point, 100 * gm::meters));
  }

  GeoIndex geo_index_out{points_out_of_circle};
  ASSERT_FALSE(geo_index_out.HasPointsInCircle(center, radius));
  ASSERT_TRUE(geo_index_out.HasPointsInCircle(center, radius + 5 * gm::meters));

  for (const auto& point : points_in_circle) {
    auto points_all_out_1_in = points_out_of_circle;
    points_all_out_1_in.push_back(point);
    GeoIndex geo_index_all_out_1_in{points_all_out_1_in};
    ASSERT_TRUE(geo_index_all_out_1_in.HasPointsInCircle(center, radius));
  }
}
