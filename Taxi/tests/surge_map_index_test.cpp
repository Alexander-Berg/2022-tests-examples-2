#include <gtest/gtest.h>

#include <hex-grid-heatmap/hex_grids_index.hpp>
#include <hex-grid-heatmap/value_hex_grid.hpp>

namespace {
using hex_grid_heatmap::HexGridIdx;
using Index =
    hex_grid_heatmap::HexGridsIndex<hex_grid_heatmap::ValueHexGrid<double>>;

const Index::Box kBox = {{32.15 * ::geometry::lon, 51.12 * ::geometry::lat},
                         {35.15 * ::geometry::lon, 58.12 * ::geometry::lat},
                         false};
const double kCellSizeMeter = 500.123;
const Index::Point kPoint{32.151 * ::geometry::lon, 51.121 * ::geometry::lat};
}  // namespace

TEST(HexGridsIndexDanglingReferences, Test) {
  Index::Grids grids{{kBox, kCellSizeMeter}};
  grids.back().map_values = {
      {HexGridIdx::ConstructUnsafe(0, 1), 1.2},
  };

  Index map{Index::Data{grids}};
  Index moved_map{std::move(map)};
  const auto* grid_moved = moved_map.FindClosestInOpt(kBox);
  ASSERT_TRUE(!!grid_moved);
  const auto& grid_moved_from_data = moved_map.GetData().grids.front();
  ASSERT_EQ(&grid_moved_from_data, grid_moved);
  const auto& hex_moved = grid_moved->GetValueHexagon(kPoint);
  ASSERT_TRUE(!!hex_moved);

  const auto& value_moved = hex_moved->value;
  ASSERT_TRUE(!!value_moved);
  ASSERT_FLOAT_EQ(*value_moved, 1.2);
}

TEST(SurgeMapIndexSearch, Test) {
  Index::Grids grids{{kBox, kCellSizeMeter}};
  grids.back().map_values = {
      {HexGridIdx::ConstructUnsafe(0, 1), 1.2},
  };

  Index map{Index::Data{grids}};
  const auto& value = map.FindValueByPoint(kPoint);
  ASSERT_TRUE(!!value);
  ASSERT_FLOAT_EQ(*value, 1.2);
}

TEST(SurgeMapIndexSearchIntersected, TestCore) {
  Index::Grids grids{{kBox, kCellSizeMeter}, {kBox, kCellSizeMeter}};
  grids.front().map_values = {
      {HexGridIdx::ConstructUnsafe(0, 1), 1.2},
  };

  Index map{Index::Data{grids}};
  const auto& value = map.FindValueByPoint(kPoint);
  ASSERT_TRUE(!!value);
  ASSERT_FLOAT_EQ(*value, 1.2);

  const Index::Point kAnotherPoint{33 * ::geometry::lon, 55 * ::geometry::lat};
  const auto& another_value = map.FindValueByPoint(kAnotherPoint);
  ASSERT_TRUE(!another_value);
}
