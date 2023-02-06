#include <gtest/gtest.h>

#include "controllers/matchers/max_cardinality.hpp"

namespace cm = controllers::matchers;

TEST(MaxCardinality, Simple) {
  for (size_t i = 5; i != 10; ++i) {
    cm::MaxCardinalityMatcher matcher(i);
    for (size_t from = 0; from != i; ++from) {
      for (size_t to = 0; to != i; ++to) {
        if (from == to) continue;
        matcher.AddEdge(from, to, 1.0);
      }
    }
    auto res = matcher.Match();
    EXPECT_EQ(res.size(), i / 2 + (i % 2));

    std::vector<bool> checks(i, false);
    for (const auto& match : res) {
      EXPECT_FALSE(match.empty());
      for (const auto& m : match) {
        EXPECT_FALSE(checks.at(m));
        checks[m] = true;
      }
    }
  }
}
