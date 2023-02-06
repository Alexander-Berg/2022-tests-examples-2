#include <unordered_set>

#include <gtest/gtest.h>
#include <boost/geometry/algorithms/disjoint.hpp>
#include <boost/geometry/index/rtree.hpp>

#include <surge/models/hex_grid.hpp>
#include <utils/geometry.hpp>

TEST(HexGrid, IdxesIn) {
  using namespace surge::models;

  using box_t = boost::geometry::model::box<utils::geometry::Point>;
  using RTreeValue = std::pair<box_t, HexGrid::Idx>;
  using RTreeIndex =
      boost::geometry::index::rtree<RTreeValue,
                                    boost::geometry::index::rstar<16>>;

  const HexGrid::Box kBox = {{32.15, 51.12}, {33.15, 53.12}};
  const double kCellSizeMeter = 500.123;
  const std::string kBaseClass = "econom";

  HexGrid grid(kBox, kCellSizeMeter, kBaseClass);

  RTreeIndex grid_index;
  {
    std::vector<RTreeValue> index_contents;

    for (size_t x = 0; x != grid.LengthX(); ++x) {
      for (size_t y = 0; y != grid.LengthY(); ++y) {
        auto hexagon = grid.GetHexagon(x, y);
        if (hexagon.IsEmpty()) {
          continue;
        }
        index_contents.emplace_back(hexagon.Envelope(), HexGrid::Idx{x, y});
      }
    }

    grid_index = RTreeIndex(index_contents);
  }

  HexGrid::Box testing_envelope = {{32.55, 51.50}, {32.60, 51.60}};

  std::unordered_set<HexGrid::Idx> expected;
  {
    std::vector<RTreeValue> filt_res;
    grid_index.query(boost::geometry::index::intersects(testing_envelope),
                     std::back_inserter(filt_res));

    for (const auto& value : filt_res) {
      auto hex_polygon = grid.GetHexagon(value.second).GetPolygon();
      if (boost::geometry::intersects(hex_polygon, testing_envelope)) {
        expected.insert(value.second);
      }
    }
  }

  std::unordered_set<HexGrid::Idx> got;
  {
    auto idxes = grid.IdxesIn(testing_envelope);
    std::vector<HexGrid::Idx> res(idxes.begin(), idxes.end());
    got.insert(res.begin(), res.end());

    EXPECT_EQ(got.size(), res.size());
  }

  ASSERT_EQ(expected, got);
}
