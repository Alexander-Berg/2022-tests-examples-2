#include "expirable.hpp"

#include <gtest/gtest.h>

using ExpirableCache = utils::caches::Expirable<int>;

TEST(ExpirableCache, Single) {
  ExpirableCache cache(std::chrono::seconds(10));
  const ExpirableCache::Value* value = nullptr;

  EXPECT_TRUE(cache.empty());

  EXPECT_EQ(nullptr, cache.Get("a"));

  const auto ts =
      ExpirableCache::Timestamp::clock::now() - std::chrono::seconds(60);
  EXPECT_TRUE(cache.Put("a", 0, ts));
  EXPECT_EQ(1, cache.size());
  value = cache.Get("a", ts);
  ASSERT_NE(nullptr, value);
  EXPECT_EQ(0, *value);

  EXPECT_FALSE(cache.Put("a", 1, ts));
  EXPECT_EQ(1, cache.size());
  value = cache.Get("a", ts);
  ASSERT_NE(nullptr, value);
  EXPECT_EQ(0, *value);

  EXPECT_FALSE(cache.Put("a", 1, ts + std::chrono::seconds(1)));
  EXPECT_EQ(1, cache.size());
  value = cache.Get("a", ts);
  ASSERT_NE(nullptr, value);
  EXPECT_EQ(1, *value);

  EXPECT_EQ(nullptr, cache.Get("a", ts + std::chrono::seconds(60)));

  cache.Cleanup();
  EXPECT_TRUE(cache.empty());
}

TEST(ExpirableCache, SizeLimit) {
  ExpirableCache cache(std::chrono::seconds(10), 1);

  EXPECT_TRUE(cache.Put("a", 0));
  EXPECT_EQ(1, cache.size());

  EXPECT_TRUE(cache.Put("b", 1));
  EXPECT_EQ(1, cache.size());
  EXPECT_EQ(nullptr, cache.Get("a"));

  EXPECT_TRUE(cache.Put("c", 2));
  EXPECT_EQ(1, cache.size());
  EXPECT_EQ(nullptr, cache.Get("b"));

  auto value = cache.Get("c");
  ASSERT_NE(nullptr, value);
  EXPECT_EQ(2, *value);
}
