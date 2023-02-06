#ifdef USERVER
#include <userver/utest/utest.hpp>
#else
#include <gtest/gtest.h>  // Y_IGNORE
#endif

#include <experiments3_common/utils/geometry.hpp>

namespace {

using Polygon = ::experiments3::geometry::utils::Polygon;
using Point = ::utils::geometry::Point;

std::vector<std::vector<Point>> CreateGrid(const Point& center,
                                           double cell_size, int n_cells) {
  std::vector<std::vector<Point>> grid;
  for (int ci = -n_cells; ci <= n_cells; ++ci) {
    std::vector<Point> line;
    for (int cj = -n_cells; cj <= n_cells; ++cj) {
      auto point =
          Point(center.lon + ci * cell_size, center.lat + cj * cell_size);
      line.push_back(point);
    }
    grid.push_back(line);
  }
  return grid;
}

}  // namespace

TEST(TestGeometryPolygon, TestIsPointInPolygon) {
  auto center = Point(37.5, 55.5);
  auto cell_size = 0.01;
  auto n_cells = 25;
  auto grid = CreateGrid(center, cell_size, n_cells);

  std::vector<Point> vertices = {grid[5][5], grid[45][5], grid[45][45],
                                 grid[19][37], grid[5][5]};
  Polygon polygon(vertices);

  for (const auto& line : grid) {
    for (const auto& point : line) {
      ASSERT_EQ(::experiments3::utils::PointInPolygon(point, vertices),
                polygon.IsPointInPolygon(point));
    }
  }
}
