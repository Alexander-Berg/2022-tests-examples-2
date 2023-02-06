
#include <gtest/gtest.h>

#include "clients/routing/router_types.hpp"
#include "geometry/position.hpp"
#include "matrix_helpers.hpp"

using Points = clients::routing::Points;
using Point = clients::routing::Point;
using clients::routing::MatrixInfo;
using clients::routing::RouterVehicleType;

TEST(MatrixHelpers, SplitVectorIntoBatches) {
  using namespace ::geometry::literals;
  Point a = {2.0_lon, 3.0_lat};
  Point b = {3.0_lon, 4.0_lat};
  Point c = {4.0_lon, 5.0_lat};

  Points points = {a, a, a, a, b, b, b, b, c, c};

  {
    auto splited_points = clients::routing::SplitVectorIntoBatches(points, 4);

    ASSERT_EQ(splited_points.size(), 3);

    Points first_batch = {a, a, a, a};
    ASSERT_EQ(splited_points[0], first_batch);

    Points second_batch = {b, b, b, b};
    ASSERT_EQ(splited_points[1], second_batch);

    Points third_banch = {c, c};
    ASSERT_EQ(splited_points[2], third_banch);
  }

  {
    auto splited_points = clients::routing::SplitVectorIntoBatches(points, 3);

    ASSERT_EQ(splited_points.size(), 4);
    Points first_batch = {a, a, a};
    ASSERT_EQ(splited_points[0], first_batch);

    Points second_batch = {a, b, b};
    ASSERT_EQ(splited_points[1], second_batch);

    Points third_banch = {b, b, c};
    ASSERT_EQ(splited_points[2], third_banch);

    Points fourth_banch = {c};
    ASSERT_EQ(splited_points[3], fourth_banch);
  }

  {
    using geometry::Latitude;
    using geometry::Longitude;

    Points points;
    for (double shift = 0.0; shift < 0.75; shift += 0.1) {
      points.emplace_back(Latitude(55.0 + shift), Longitude(37.0));
    }

    ASSERT_EQ(points.size(), 8);

    {
      const auto batches = clients::routing::SplitVectorIntoBatches(points, 3);
      std::vector<Points> expected_batches;
      expected_batches.push_back({
          {Latitude(55.0), Longitude(37.0)},
          {Latitude(55.1), Longitude(37.0)},
          {Latitude(55.2), Longitude(37.0)},
      });
      expected_batches.push_back({
          {Latitude(55.3), Longitude(37.0)},
          {Latitude(55.4), Longitude(37.0)},
          {Latitude(55.5), Longitude(37.0)},
      });
      expected_batches.push_back({
          {Latitude(55.6), Longitude(37.0)},
          {Latitude(55.7), Longitude(37.0)},
      });
      EXPECT_EQ(batches, expected_batches);
    }

    {
      const auto batches = clients::routing::SplitVectorIntoBatches(points, 4);
      std::vector<Points> expected_batches;
      expected_batches.push_back({
          {Latitude(55.0), Longitude(37.0)},
          {Latitude(55.1), Longitude(37.0)},
          {Latitude(55.2), Longitude(37.0)},
          {Latitude(55.3), Longitude(37.0)},
      });
      expected_batches.push_back({
          {Latitude(55.4), Longitude(37.0)},
          {Latitude(55.5), Longitude(37.0)},
          {Latitude(55.6), Longitude(37.0)},
          {Latitude(55.7), Longitude(37.0)},
      });
      EXPECT_EQ(batches, expected_batches);
    }
  }
}

TEST(MatrixHelpers, UniteTaskResultsIntoOneMatrix) {
  auto CreateMxNMatrixInfo = [](size_t rows,
                                size_t columns) -> narray::Array2D<MatrixInfo> {
    std::vector<MatrixInfo> info(rows * columns);
    for (size_t row_id = 0; row_id < rows; ++row_id) {
      for (size_t column_id = 0; column_id < columns; ++column_id) {
        info[row_id * columns + column_id].src_point_idx = row_id;
        info[row_id * columns + column_id].dst_point_idx = column_id;
      }
    }
    return narray::Array2D<MatrixInfo>(std::move(info), columns);
  };

  // Let's create 5x7 matrix batched with batch size 3
  std::vector<std::vector<narray::Array2D<MatrixInfo>>> grid;
  grid.push_back({CreateMxNMatrixInfo(3, 3), CreateMxNMatrixInfo(3, 3),
                  CreateMxNMatrixInfo(3, 1)});
  grid.push_back({CreateMxNMatrixInfo(2, 3), CreateMxNMatrixInfo(2, 3),
                  CreateMxNMatrixInfo(2, 1)});

  const auto actual_data = clients::routing::UniteTaskResultsIntoOneMatrix(
      std::move(grid), std::vector<Point>(5), std::vector<Point>(7), 3);

  // Now create big 5x7 matrix
  const auto expected_matrix = CreateMxNMatrixInfo(5, 7);
  const auto& expected_data = expected_matrix.GetUnderlying();

  ASSERT_EQ(expected_data.size(), actual_data.size());
  for (size_t i = 0; i < actual_data.size(); ++i) {
    ASSERT_EQ(expected_data[i].src_point_idx, actual_data[i].src_point_idx);
    ASSERT_EQ(expected_data[i].dst_point_idx, actual_data[i].dst_point_idx);
  }
}
