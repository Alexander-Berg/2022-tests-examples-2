#include "heap_dict.hpp"

#include <gtest/gtest.h>

TEST(HeapDictSimple, One) {
  utils::HeapDict<int, int> d;

  d.push(1, 3);
  EXPECT_EQ(d.top().first, 1);

  d.push(2, 6);
  d.push(3, 4);
  EXPECT_EQ(d.top().first, 2);

  d.push(4, 10);
  EXPECT_EQ(d.top().first, 4);

  d[4] = 5;
  EXPECT_EQ(d.top().first, 2);

  d.pop();
  EXPECT_EQ(d.top().first, 4);

  d.pop();
  EXPECT_EQ(d.top().first, 3);
  EXPECT_EQ(d.size(), 2u);

  d.erase(d.find(1));
  EXPECT_EQ(d.top().first, 3);
  EXPECT_EQ(d.size(), 1u);
}
