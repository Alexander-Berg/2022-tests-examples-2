#include <gtest/gtest.h>
#include <limits>

#include <models/geometry/point.hpp>
#include <models/order_meta.hpp>

#include <controllers/neighbours_searcher.hpp>

namespace combo_matcher {

TEST(FindNeighbours, Simple) {
  using ::models::geometry::Point;
  std::vector<::models::geometry::Point> points{{92.865575, 55.986885},
                                                {39.051504, 45.033745},
                                                {30.370960, 60.050888},
                                                {30.206501, 59.999286}};
  std::vector<combo_matcher::models::OrderMeta> orders;
  for (const auto& point : points) {
    combo_matcher::models::OrderMeta order_meta;
    order_meta.point = point;
    orders.emplace_back(order_meta);
  }

  ::controllers::NeighboursSearcher neighbour_processor(orders);

  std::vector<models::MatchCandidatesIdxs> candidates;

  // Distance between 2-nd and 3-rd points is ~10.8km
  candidates = neighbour_processor(10000);
  EXPECT_EQ(candidates.size(), 0);
  candidates = neighbour_processor(11000);
  EXPECT_EQ(candidates.size(), 1);
  EXPECT_EQ(candidates[0], models::MatchCandidatesIdxs(2, 3));

  // max distance
  candidates = neighbour_processor(std::numeric_limits<size_t>::max());
  EXPECT_EQ(candidates.size(), 6);  // C(4, 2) = 6
}

}  // namespace combo_matcher
