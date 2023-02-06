#include <graph/route_conversion.hpp>

#include <gtest/gtest.h>

namespace graph {

TEST(RouteConversion, FromIdContainer) {
  std::vector<unsigned int> test_ids{0u, 1u, 2l, 3u, 4u};
  const auto route = conversion::ToRoute(test_ids, false);

  EXPECT_EQ(test_ids.size(), std::distance(route.begin(), route.end()));

  const auto route_reversed = conversion::ToRoute(test_ids, true);

  EXPECT_EQ(test_ids.size(),
            std::distance(route_reversed.begin(), route_reversed.end()));
}

}  // namespace graph
