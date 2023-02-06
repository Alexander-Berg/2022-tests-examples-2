#include <gtest/gtest.h>

#include <models/heatmap/hex_grid_idx_adjency_matrix.hpp>

TEST(HexGridIdxAdjencyMatrix, Test) {
  const size_t depth = 3;
  models::heatmap::HexGridIdxAdjacencyMatrix adjecency_matrix(depth);
  auto idx = hex_grid_heatmap::HexGridIdx::ConstructUnsafe(10, 10);

  auto adjacent = adjecency_matrix.GetAdjacent(idx);

  auto any_adj_from_left =
      std::find_if(adjacent.begin(), adjacent.end(),
                   [&idx](const auto& adj_idx) { return adj_idx.x < idx.x; });
  ASSERT_NE(any_adj_from_left, adjacent.end());
}
