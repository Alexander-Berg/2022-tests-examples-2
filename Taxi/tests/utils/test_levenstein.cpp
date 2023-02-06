#include <gtest/gtest.h>

#include "utils/levenstein.hpp"

TEST(TestLevenstein, SimpleCompare) {
  auto lev = persuggest::levenstein::LevensteinDistance("abracadabra", "ada");
  ASSERT_EQ(lev.highlight.size(), 1);
  ASSERT_EQ(lev.eq_length, 3);
  ASSERT_EQ(lev.highlight[0].first, 5);
  ASSERT_EQ(lev.highlight[0].second, 8);
  lev = persuggest::levenstein::LevensteinDistance("abracadabra", "cda");
  ASSERT_EQ(lev.highlight.size(), 2);
  ASSERT_EQ(lev.eq_length, 3);
  ASSERT_EQ(lev.highlight[0].first, 4);
  ASSERT_EQ(lev.highlight[0].second, 5);
  ASSERT_EQ(lev.highlight[1].first, 6);
  ASSERT_EQ(lev.highlight[1].second, 8);
  lev = persuggest::levenstein::LevensteinDistance("abracadabra", "сda", 1);
  ASSERT_EQ(lev.highlight.size(), 1);
  ASSERT_EQ(lev.eq_length, 2);
  ASSERT_EQ(lev.highlight[0].first, 6);
  ASSERT_EQ(lev.highlight[0].second, 8);
}
