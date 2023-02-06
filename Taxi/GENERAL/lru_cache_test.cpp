#include <gtest/gtest.h>

#include "lru_cache.hpp"

TEST(edge_drivers_cache_impl, lru_cache) {
  using LRUCache = caches::LRUCache<uint32_t, uint64_t>;

  {
    LRUCache lru;
    lru.Insert(0, 0);
    lru.Insert(1, 1);
    lru.Insert(2, 2);
    lru.Insert(3, 3);
    // test inserted
    ASSERT_EQ(4ull, lru.Size());
    ASSERT_EQ(0ull, lru.GetNonUpdate(0));
    ASSERT_EQ(1ull, lru.GetNonUpdate(1));
    ASSERT_EQ(2ull, lru.GetNonUpdate(2));
    ASSERT_EQ(3ull, lru.GetNonUpdate(3));

    lru.SetMaxSize(0);
    ASSERT_EQ(0ull, lru.Size());
  }

  {
    LRUCache lru;
    lru.Insert(0, 0);
    lru.Insert(1, 1);
    lru.Insert(2, 2);
    lru.Insert(3, 3);

    lru.SetMaxSize(2);
    ASSERT_EQ(2ull, lru.GetNonUpdate(2));
    ASSERT_EQ(3ull, lru.GetNonUpdate(3));
    ASSERT_EQ(2ull, lru.Size());
  }

  {
    LRUCache lru;
    lru.Insert(0, 0);
    lru.Insert(1, 1);
    lru.Insert(2, 2);
    lru.Insert(3, 3);
    // insert same key multiple times
    lru.Insert(0, 0);
    lru.Insert(0, 0);
    lru.Insert(0, 0);

    lru.SetMaxSize(2);
    ASSERT_EQ(0ull, lru.GetNonUpdate(0));
    ASSERT_EQ(3ull, lru.GetNonUpdate(3));
    ASSERT_EQ(2ull, lru.Size());

    lru.SetMaxSize(1);
    ASSERT_EQ(1ull, lru.Size());
    ASSERT_EQ(0ull, lru.GetNonUpdate(0));
  }

  {
    LRUCache lru;
    lru.SetMaxSize(2);
    lru.Insert(0, 0);
    lru.Insert(1, 1);
    lru.Insert(2, 2);
    lru.Insert(3, 3);

    ASSERT_EQ(2ull, lru.Size());
    ASSERT_TRUE(lru.HasKey(2));
    ASSERT_TRUE(lru.HasKey(3));
  }

  {
    LRUCache lru;
    lru.SetMaxSize(2);
    lru.Insert(0, 0);
    lru.Insert(1, 1);
    lru.Get(0);  // Update
    lru.Insert(2, 2);
    lru.Get(0);  // Update
    lru.Insert(3, 3);

    ASSERT_EQ(2ull, lru.Size());
    ASSERT_TRUE(lru.HasKey(0));  // was updated
    ASSERT_TRUE(lru.HasKey(3));
  }

  {
    LRUCache lru;
    lru.Insert(0, 0);
    lru.Insert(1, 1);
    lru.Insert(2, 2);
    lru.Insert(3, 3);
    // test inserted
    ASSERT_EQ(4ull, lru.Size());
    ASSERT_FALSE(lru.HasKey(5));
    // get missing key, value will be generated
    const auto res1 = lru.Get(5, [](const auto&) { return 5ull; });
    ASSERT_EQ(5ull, res1);
    // now we have the key in cache, so functor ignored. Cached value returned
    const auto res2 = lru.Get(5, [](const auto&) { return 42ull; });
    ASSERT_EQ(5ull, res2);

    lru.SetMaxSize(0);
    ASSERT_EQ(0ull, lru.Size());
  }
}
