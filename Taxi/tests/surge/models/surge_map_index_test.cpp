#include <sstream>

#include <gtest/gtest.h>

#include <common/surge_test_common.hpp>
#include <surge/models/surge_map_index_benchmark_utils.hpp>

namespace {
surge::models::SurgeValueMapIndex::Grids GetNonIntersectingGrids() {
  auto grids = benchmark::surge_map_index::Grids();
  // remove intersecting bboxes:
  if (grids.size() > 91) {
    grids.erase(grids.begin() + 12);
    grids.erase(grids.begin() + 91);
  }
  return grids;
}

std::string ErrorMessage(
    time_t seed, const surge::models::SurgeValueMapIndex::Point& point,
    const surge::models::SurgeValueMapIndex::Box* box = nullptr) {
  std::stringstream ss;
  ss << "SEED: " << seed << " POINT: " << point;
  if (box) {
    ss << " BOX: " << *box;
  }
  return ss.str();
}

}  // namespace

TEST(SurgeMapIndexFindByPoint, Test) {
  const auto seed = time(nullptr);
  srand(seed);
  const auto points = benchmark::surge_map_index::GeneratePoints(10);
  const auto grids = GetNonIntersectingGrids();

  const surge::models::SurgeValueMapIndex rtree_index{
      surge::models::SurgeValueMapIndex::Data{grids}};
  const surge::models::benchmark::SurgeValueMapIndex linear_index{grids};

  for (const auto& point : points) {
    const auto rtree_found_grid = rtree_index.FindByPoint(point);
    const auto linear_found_grid = linear_index.FindByPoint(point);

    ASSERT_EQ(rtree_found_grid.is_initialized(),
              linear_found_grid.is_initialized())
        << ErrorMessage(seed, point);
    if (rtree_found_grid.is_initialized()) {
      ASSERT_TRUE(surge::models::AreEuqal<surge::models::SurgeValue>(
          *rtree_found_grid, *linear_found_grid))
          << ErrorMessage(seed, point);
    }
  }
}

TEST(SurgeMapIndexFindClosestIn, Test) {
  const auto seed = time(nullptr);
  srand(seed);
  using namespace benchmark::surge_map_index;
  using namespace surge::models;
  const auto boxes = GenerateBoxes(10);
  const auto points = GeneratePoints(boxes);
  const auto grids = GetNonIntersectingGrids();

  const surge::models::SurgeValueMapIndex rtree_index{
      surge::models::SurgeValueMapIndex::Data{grids}};
  const surge::models::benchmark::SurgeValueMapIndex linear_index{grids};
  for (unsigned long i = 0; i < boxes.size(); ++i) {
    const auto point =
        boost::optional<surge::models::SurgeValueMapIndex::Point>{points[i]};
    const auto& box = boxes[i];
    const auto rtree_found_grid = rtree_index.FindClosestIn(box, point);
    const auto linear_found_grid = linear_index.FindClosestIn(box, point);

    ASSERT_EQ(rtree_found_grid.is_initialized(),
              linear_found_grid.is_initialized())
        << ErrorMessage(seed, *point, &box);
    if (rtree_found_grid.is_initialized()) {
      ASSERT_TRUE(surge::models::AreEuqal<surge::models::SurgeValue>(
          *rtree_found_grid, *linear_found_grid))
          << ErrorMessage(seed, *point, &box);
    }
  }
}

TEST(SurgeMapIndexDanglingReferences, Test) {
  using surge::models::SurgeValueMapIndex;
  using HexGrid = SurgeValueMapIndex::Grid;

  const HexGrid::Box kBox = {{32.15, 51.12}, {35.15, 58.12}};
  const double kCellSizeMeter = 500.123;
  const std::string kBaseClass = "econom";

  std::vector<HexGrid> grids{{kBox, kCellSizeMeter, kBaseClass}};
  grids.back().surge_map_values = {{"__default__",
                                    {
                                        {{0, 0}, {1.2, 1.0, {}}},
                                    }}};

  std::shared_ptr<surge::models::SurgeValueMapIndex> surge_map =
      std::make_shared<surge::models::SurgeValueMapIndex>(
          surge::models::SurgeValueMapIndex::Data{grids});
  surge::models::SurgeValueMapIndex moved_surge_map{std::move(*surge_map)};
  const auto& grid_moved =
      moved_surge_map.FindByPoint(utils::geometry::Point{32.151, 51.121});
  ASSERT_TRUE(!!grid_moved);
  const auto& grid_moved_from_data = moved_surge_map.GetData().grids.front();
  ASSERT_EQ(&grid_moved_from_data, &*grid_moved);
  const auto& value_moved =
      grid_moved->GetValueHexagon(utils::geometry::Point{32.151, 51.121}).value;
  ASSERT_TRUE(!!value_moved);
  ASSERT_FLOAT_EQ(value_moved->surge, 1.2);
}

TEST(SurgeMapIndexSearchBaseClass, Test) {
  using surge::models::SurgeValueMapIndex;
  using HexGrid = SurgeValueMapIndex::Grid;

  const HexGrid::Box kBox = {{32.15, 51.12}, {35.15, 58.12}};
  const double kCellSizeMeter = 500.123;
  const std::string kBaseClass = "econom";

  std::vector<HexGrid> grids{{kBox, kCellSizeMeter, kBaseClass}};
  grids.back().surge_map_values = {{"__default__",
                                    {
                                        {{0, 0}, {1.2, 1.0, {}}},
                                    }}};

  surge::models::SurgeValueMapIndex surge_map{
      surge::models::SurgeValueMapIndex::Data{grids}};
  const auto& value = surge_map.FindValueByPoint(
      utils::geometry::Point{32.151, 51.121}, kBaseClass);
  ASSERT_TRUE(!!value);
  ASSERT_FLOAT_EQ(value->surge, 1.2);
}

TEST(SurgeMapIndexSearchIntersected, TestCore) {
  using surge::models::SurgeValueMapIndex;
  using HexGrid = SurgeValueMapIndex::Grid;

  const HexGrid::Box kBox = {{32.15, 51.12}, {35.15, 58.12}};
  const double kCellSizeMeter = 500.123;
  const std::string kBaseClass = "econom";

  std::vector<HexGrid> grids{{kBox, kCellSizeMeter, kBaseClass},
                             {kBox, kCellSizeMeter, kBaseClass}};
  grids.front().surge_map_values = {{"__default__",
                                     {
                                         {{0, 0}, {1.2, 1.0, {}}},
                                     }}};

  surge::models::SurgeValueMapIndex surge_map{
      surge::models::SurgeValueMapIndex::Data{grids}};
  const auto& value = surge_map.FindValueByPoint(
      utils::geometry::Point{32.151, 51.121}, kBaseClass);
  ASSERT_TRUE(!!value);
  ASSERT_FLOAT_EQ(value->surge, 1.2);
}
