#include "sharded_concurrent_map.hpp"

#include <gtest/gtest.h>
#include <array>

using Map = threads::ShardedConcurrentMap<uint32_t, uint32_t>;
const uint32_t kTestCount = 16;

TEST(ShardedConcurrentMap, Push) {
  Map map;
  for (uint32_t i = 0; i < kTestCount; ++i) map.Push(i, i);

  EXPECT_EQ(kTestCount, map.Size());
}

TEST(ShardedConcurrentMap, Get) {
  Map map;
  for (uint32_t i = 0; i < kTestCount; ++i) map.Push(i, i);

  ASSERT_EQ(kTestCount, map.Size());

  for (uint32_t i = 0; i < kTestCount; ++i) EXPECT_EQ(i, map.Get(i));
  for (uint32_t i = 0; i < kTestCount; ++i) EXPECT_EQ(i, map.Get(i, 0));

  EXPECT_THROW(map.Get(kTestCount), std::out_of_range);
  EXPECT_EQ(0u, map.Get(kTestCount, 0));

  EXPECT_EQ(kTestCount, map.Size());
}

TEST(ShardedConcurrentMap, Pop) {
  Map map;
  for (uint32_t i = 0; i < kTestCount; ++i) map.Push(i, i);

  ASSERT_EQ(kTestCount, map.Size());

  for (uint32_t i = 0; i < kTestCount; ++i) EXPECT_EQ(i, map.Pop(i));

  EXPECT_EQ(0u, map.Size());

  EXPECT_THROW(map.Pop(kTestCount), std::out_of_range);
  EXPECT_EQ(0u, map.Pop(kTestCount, 0));
}

TEST(ShardedConcurrentMap, Clear) {
  Map map;
  for (uint32_t i = 0; i < kTestCount; ++i) map.Push(i, i);

  ASSERT_EQ(kTestCount, map.Size());

  map.Clear();
  EXPECT_EQ(0u, map.Size());
}

TEST(ShardedConcurrentMap, PopGroup) {
  Map map;
  for (uint32_t i = 0; i < kTestCount; ++i) map.Push(i, i);

  ASSERT_EQ(kTestCount, map.Size());

  std::set<uint32_t> keys;
  std::vector<std::pair<uint32_t, uint32_t>> values;

  for (uint32_t i = 0; i < kTestCount; ++i)
    if (i % 2) keys.insert(i);

  values = map.Pop(keys, 0);
  ASSERT_EQ(keys.size(), values.size());
  EXPECT_EQ(kTestCount - keys.size(), map.Size());
  for (const auto& pair : values) EXPECT_EQ(pair.first, pair.second);

  keys.clear();
  values.clear();
  for (uint32_t i = 0; i < kTestCount; ++i) keys.insert(i);
  values = map.Pop(keys, 0);
  ASSERT_EQ(keys.size(), values.size());
  EXPECT_EQ(0u, map.Size());
  for (const auto& pair : values) {
    if (pair.first % 2)
      EXPECT_EQ(0u, pair.second);
    else
      EXPECT_EQ(pair.first, pair.second);
  }
}
