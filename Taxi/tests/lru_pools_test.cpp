#include <utils/lru_pools.hpp>

#include <algorithm>
#include <vector>

#include <gtest/gtest.h>

namespace {

using LruPools = utils::LruPools<int>;

template <class Span, class... Args>
void ExpectValues(Span result, Args... v) {
  std::vector<int> res(result.begin(), result.end());
  std::vector<int> ethalon = {v...};

  std::sort(res.begin(), res.end());
  std::sort(ethalon.begin(), ethalon.end());

  EXPECT_EQ(res, ethalon);
}

}  // namespace

TEST(LruPools, Insertion) {
  LruPools pools(6);
  pools.AddToPool(1, 10);
  pools.AddToPool(2, 20);
  pools.AddToPool(3, 30);

  ExpectValues(pools.GetFromPool(1), 1, 10);
  ExpectValues(pools.GetFromPool(2), 2, 20);
  ExpectValues(pools.GetFromPool(3), 3, 30);
  ASSERT_EQ(std::size(pools.GetFromPool(4)), 0);

  ExpectValues(pools.GetFromPool(10), 1, 10);
  ExpectValues(pools.GetFromPool(20), 2, 20);
  ExpectValues(pools.GetFromPool(30), 3, 30);
  ASSERT_EQ(std::size(pools.GetFromPool(40)), 0);
}

TEST(LruPools, Insertion2) {
  LruPools pools(6);
  pools.AddToPool(1, 10);
  pools.AddToPool(2, 20);
  pools.AddToPool(2, 25);

  ExpectValues(pools.GetFromPool(1), 1, 10);
  ExpectValues(pools.GetFromPool(25), 2, 20, 25);
  ExpectValues(pools.GetFromPool(20), 2, 20, 25);
  ExpectValues(pools.GetFromPool(2), 2, 20, 25);

  pools.AddToPool(27, 2);

  ExpectValues(pools.GetFromPool(1), 1, 10);
  ExpectValues(pools.GetFromPool(27), 2, 20, 25, 27);
  ExpectValues(pools.GetFromPool(25), 2, 20, 25, 27);
  ExpectValues(pools.GetFromPool(20), 2, 20, 25, 27);
  ExpectValues(pools.GetFromPool(2), 2, 20, 25, 27);
}

TEST(LruPools, Insertion3) {
  LruPools pools(6);
  pools.AddToPool(1, 10);
  pools.AddToPool(2, 20);
  pools.AddToPool(3, 30);

  pools.AddToPool(3, 30);
  pools.AddToPool(30, 3);
  pools.AddToPool(3, 30);

  ExpectValues(pools.GetFromPool(1), 1, 10);
  ExpectValues(pools.GetFromPool(2), 2, 20);
  ExpectValues(pools.GetFromPool(3), 3, 30);
  ASSERT_EQ(std::size(pools.GetFromPool(4)), 0);

  ExpectValues(pools.GetFromPool(10), 1, 10);
  ExpectValues(pools.GetFromPool(20), 2, 20);
  ExpectValues(pools.GetFromPool(30), 3, 30);
  ASSERT_EQ(std::size(pools.GetFromPool(40)), 0);
}

TEST(LruPools, Overflow) {
  LruPools pools(6);
  pools.AddToPool(1, 10);
  pools.AddToPool(2, 20);
  pools.AddToPool(3, 30);
  pools.AddToPool(4, 40);

  ASSERT_EQ(std::size(pools.GetFromPool(1)), 0);
  ExpectValues(pools.GetFromPool(2), 2, 20);
  ExpectValues(pools.GetFromPool(3), 3, 30);
  ExpectValues(pools.GetFromPool(4), 4, 40);

  ASSERT_EQ(std::size(pools.GetFromPool(1)), 0);
  ExpectValues(pools.GetFromPool(20), 2, 20);
  ExpectValues(pools.GetFromPool(30), 3, 30);
  ExpectValues(pools.GetFromPool(40), 4, 40);
}

TEST(LruPools, OverflowSinglePool1) {
  LruPools pools(2);
  pools.AddToPool(1, 10);
  pools.AddToPool(1, 20);
  pools.AddToPool(1, 30);

  size_t found = 0;
  for (auto n : {1, 10, 20, 30}) {
    ASSERT_NO_THROW(pools.GetFromPool(n)) << "For " << n;
    found += std::size(pools.GetFromPool(n)) ? 1 : 0;
  }

  EXPECT_EQ(found, 2);
}

TEST(LruPools, OverflowSinglePool2) {
  LruPools pools(3);
  pools.AddToPool(1, 10);
  pools.AddToPool(10, 20);
  pools.AddToPool(20, 30);

  size_t found = 0;
  for (auto n : {1, 10, 20, 30}) {
    ASSERT_NO_THROW(pools.GetFromPool(n)) << "For " << n;
    found += std::size(pools.GetFromPool(n)) ? 1 : 0;
  }

  EXPECT_EQ(found, 3);
}

TEST(LruPools, Use) {
  LruPools pools(6);
  pools.AddToPool(1, 10);
  pools.AddToPool(2, 20);
  pools.AddToPool(3, 30);
  ExpectValues(pools.GetFromPool(1), 1, 10);
  pools.AddToPool(4, 40);

  ExpectValues(pools.GetFromPool(1), 1, 10);
  ASSERT_EQ(std::size(pools.GetFromPool(2)), 0);
  ExpectValues(pools.GetFromPool(3), 3, 30);
  ExpectValues(pools.GetFromPool(4), 4, 40);

  ExpectValues(pools.GetFromPool(10), 1, 10);
  ASSERT_EQ(std::size(pools.GetFromPool(20)), 0);
  ExpectValues(pools.GetFromPool(30), 3, 30);
  ExpectValues(pools.GetFromPool(40), 4, 40);
}

TEST(LruPools, PoolsMerge) {
  LruPools pools(6);
  pools.AddToPool(1, 10);
  pools.AddToPool(2, 20);
  pools.AddToPool(3, 30);

  pools.AddToPool(1, 2);
  ASSERT_EQ(std::size(pools.GetFromPool(1)), 4);
  ASSERT_EQ(std::size(pools.GetFromPool(2)), 4);
  ASSERT_EQ(std::size(pools.GetFromPool(10)), 4);
  ASSERT_EQ(std::size(pools.GetFromPool(20)), 4);

  ExpectValues(pools.GetFromPool(3), 3, 30);
  ExpectValues(pools.GetFromPool(30), 3, 30);

  pools.AddToPool(2, 3);
  ASSERT_EQ(std::size(pools.GetFromPool(1)), 6);
  ASSERT_EQ(std::size(pools.GetFromPool(2)), 6);
  ASSERT_EQ(std::size(pools.GetFromPool(3)), 6);
  ASSERT_EQ(std::size(pools.GetFromPool(10)), 6);
  ASSERT_EQ(std::size(pools.GetFromPool(20)), 6);
  ASSERT_EQ(std::size(pools.GetFromPool(30)), 6);
}

TEST(LruPools, PoolsMergeUse) {
  LruPools pools(6);
  pools.AddToPool(1, 10);
  pools.AddToPool(2, 20);
  pools.AddToPool(3, 30);

  pools.AddToPool(1, 2);
  pools.AddToPool(4, 40);
  ASSERT_EQ(std::size(pools.GetFromPool(3)), 0);
  ASSERT_EQ(std::size(pools.GetFromPool(30)), 0);
  ASSERT_EQ(std::size(pools.GetFromPool(10)), 4);
  ASSERT_EQ(std::size(pools.GetFromPool(20)), 4);
  ASSERT_EQ(std::size(pools.GetFromPool(1)), 4);
  ASSERT_EQ(std::size(pools.GetFromPool(2)), 4);

  pools.AddToPool(5, 50);
  ASSERT_EQ(std::size(pools.GetFromPool(4)), 0);
  ASSERT_EQ(std::size(pools.GetFromPool(40)), 0);
  ASSERT_EQ(std::size(pools.GetFromPool(10)), 4);
  ASSERT_EQ(std::size(pools.GetFromPool(20)), 4);
  ASSERT_EQ(std::size(pools.GetFromPool(1)), 4);
  ASSERT_EQ(std::size(pools.GetFromPool(2)), 4);

  ExpectValues(pools.GetFromPool(50), 5, 50);
  ExpectValues(pools.GetFromPool(5), 5, 50);
}

TEST(LruPools, PoolsErase) {
  LruPools pools(6);
  pools.AddToPool(1, 10);
  pools.AddToPool(2, 20);
  pools.AddToPool(3, 30);

  pools.ErasePool(10);
  ASSERT_EQ(std::size(pools.GetFromPool(1)), 0);
  ASSERT_EQ(std::size(pools.GetFromPool(10)), 0);
  ExpectValues(pools.GetFromPool(2), 2, 20);
  ExpectValues(pools.GetFromPool(3), 3, 30);
  ExpectValues(pools.GetFromPool(20), 2, 20);
  ExpectValues(pools.GetFromPool(30), 3, 30);

  pools.ErasePool(2);
  ASSERT_EQ(std::size(pools.GetFromPool(1)), 0);
  ASSERT_EQ(std::size(pools.GetFromPool(10)), 0);
  ASSERT_EQ(std::size(pools.GetFromPool(2)), 0);
  ASSERT_EQ(std::size(pools.GetFromPool(20)), 0);
  ExpectValues(pools.GetFromPool(30), 3, 30);

  pools.AddToPool(3, 35);
  pools.AddToPool(37, 35);
  pools.ErasePool(37);
  ASSERT_EQ(std::size(pools.GetFromPool(1)), 0);
  ASSERT_EQ(std::size(pools.GetFromPool(10)), 0);
  ASSERT_EQ(std::size(pools.GetFromPool(2)), 0);
  ASSERT_EQ(std::size(pools.GetFromPool(20)), 0);
  ASSERT_EQ(std::size(pools.GetFromPool(3)), 0);
  ASSERT_EQ(std::size(pools.GetFromPool(30)), 0);
  ASSERT_EQ(std::size(pools.GetFromPool(35)), 0);
  ASSERT_EQ(std::size(pools.GetFromPool(37)), 0);
}

TEST(LruPools, BorderCases) {
  // LruPools behavior in those test is a subject to change!
  //
  // We are testing only for memory leaks/corruption here
  LruPools lru(1);

  lru.AddToPool(1, 2);
  ASSERT_LE(std::size(lru.GetFromPool(1)) + std::size(lru.GetFromPool(2)), 2);

  lru.AddToPool(1, 2);
  ASSERT_LE(std::size(lru.GetFromPool(1)) + std::size(lru.GetFromPool(2)), 2);

  lru.AddToPool(2, 1);
  ASSERT_LE(std::size(lru.GetFromPool(1)) + std::size(lru.GetFromPool(2)), 2);

  lru.AddToPool(2, 1);
  ASSERT_LE(std::size(lru.GetFromPool(1)) + std::size(lru.GetFromPool(2)), 2);

  lru.AddToPool(2, 2);
  ASSERT_EQ(std::size(lru.GetFromPool(2)), 1);

  lru.AddToPool(2, 2);
  ASSERT_EQ(std::size(lru.GetFromPool(2)), 1);

  lru.AddToPool(1, 1);
  ASSERT_EQ(std::size(lru.GetFromPool(1)), 1);

  lru.AddToPool(1, 1);
  ASSERT_EQ(std::size(lru.GetFromPool(1)), 1);

  lru.AddToPool(3, 4);
  ASSERT_LE(std::size(lru.GetFromPool(3)) + std::size(lru.GetFromPool(4)), 2);

  lru.AddToPool(4, 5);
  ASSERT_LE(std::size(lru.GetFromPool(3)) + std::size(lru.GetFromPool(4)) +
                std::size(lru.GetFromPool(5)),
            3);
}
