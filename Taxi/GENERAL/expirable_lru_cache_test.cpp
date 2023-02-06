#include <thread>

#include <gmock/gmock.h>
#include <gtest/gtest.h>

#include <utils/mock_now.hpp>

#include "expirable_lru_cache.hpp"

using utils::datetime::MockNowSet;
using utils::datetime::MockSleep;

TEST(expirable_lru_cache, expiration) {
  using Cache = caches::ExpirableLRUCache<uint32_t, uint64_t>;
  using CacheComplex =
      caches::ExpirableLRUCache<uint32_t, std::vector<uint32_t>>;

  struct ComplexKey {
    uint32_t id;
    std::string key;
  };

  struct ComplexKeyHasher {
    std::size_t operator()(const ComplexKey& key) const {
      auto hash = boost::hash_value(key.key);
      boost::hash_combine(hash, key.id);
      return hash;
    }
  };

  auto equal = [](const ComplexKey& k1, const ComplexKey& k2) -> bool {
    return k1.id == k2.id && k1.key == k2.key;
  };

  using CacheComplexKeyValue =
      caches::ExpirableLRUCache<ComplexKey, std::vector<uint32_t>,
                                ComplexKeyHasher, decltype(equal)>;

  const std::chrono::system_clock::time_point kStartTP(std::chrono::seconds(1));
  const std::chrono::seconds kSleep(10);

  {
    Cache lru;
    lru.SetMaxSize(2ul);
    lru.SetExpiration(std::chrono::milliseconds(100));
    MockNowSet(kStartTP);

    lru.Insert(0, 5ull);
    lru.Insert(1, 6ull);

    ASSERT_EQ(2ull, lru.Size());
    uint64_t value{};
    ASSERT_EQ(lru.Get(0, value), Cache::OK);
    ASSERT_EQ(value, 5ull);
    ASSERT_EQ(lru.Get(1, value), Cache::OK);
    ASSERT_EQ(value, 6ull);

    lru.Insert(2, 7ull);

    ASSERT_EQ(2ul, lru.Size());

    ASSERT_EQ(lru.Get(1, value), Cache::OK);
    ASSERT_EQ(value, 6ull);
    ASSERT_EQ(lru.Get(2, value), Cache::OK);
    ASSERT_EQ(value, 7ull);
  }

  {
    Cache lru;
    lru.SetMaxSize(2ul);
    lru.SetExpiration(std::chrono::milliseconds(2));
    MockNowSet(kStartTP);

    lru.Insert(0, 5ull);
    lru.Insert(1, 6ull);

    ASSERT_EQ(2ul, lru.Size());
    MockSleep(kSleep);
    lru.RemoveExpired();
    ASSERT_EQ(0ul, lru.Size());
  }

  {
    Cache lru;
    lru.SetMaxSize(2ul);
    lru.SetExpiration(std::chrono::milliseconds(2));
    MockNowSet(kStartTP);

    lru.Insert(0, 5ull);
    ASSERT_EQ(1ul, lru.Size());
    MockSleep(kSleep);

    lru.Insert(1, 6ull);
    ASSERT_EQ(1ul, lru.Size());
    uint64_t value{};
    ASSERT_EQ(lru.Get(1, value), Cache::OK);
    ASSERT_EQ(value, 6ull);
  }

  {
    Cache lru;
    lru.SetMaxSize(2ul);
    lru.SetExpiration(std::chrono::milliseconds(2));
    MockNowSet(kStartTP);

    lru.Insert(0, 5ull);
    lru.Insert(1, 6ull);

    ASSERT_EQ(2ul, lru.Size());
    MockSleep(kSleep);
    lru.Insert(2, 7ull);
    ASSERT_EQ(1ul, lru.Size());
    uint64_t value{};
    ASSERT_EQ(lru.Get(2, value), Cache::OK);
    ASSERT_EQ(value, 7ull);
  }

  {
    Cache lru;
    lru.SetMaxSize(2ul);
    lru.SetExpiration(std::chrono::milliseconds(1));
    MockNowSet(kStartTP);

    lru.Insert(0, 5ull);
    lru.Insert(1, 6ull);

    uint64_t value{};
    ASSERT_EQ(lru.Get(0, value), Cache::OK);
    ASSERT_EQ(value, 5ull);
    ASSERT_EQ(lru.Get(1, value), Cache::OK);
    ASSERT_EQ(value, 6ull);

    ASSERT_EQ(2ul, lru.Size());

    MockSleep(kSleep);

    ASSERT_EQ(lru.Get(0, value), Cache::EXPIRED);
    ASSERT_EQ(lru.Get(1, value), Cache::EXPIRED);

    ASSERT_EQ(lru.Get(2, value), Cache::NOT_FOUND);
    lru.Insert(2, 7ull);
    ASSERT_EQ(lru.Get(2, value), Cache::OK);
    ASSERT_EQ(value, 7ull);
  }

  {
    CacheComplex lru;
    lru.SetMaxSize(2ul);
    lru.SetExpiration(std::chrono::milliseconds(100));
    MockNowSet(kStartTP);

    lru.Insert(0, {5ull});
    lru.Insert(1, {6ull});

    ASSERT_EQ(2ul, lru.Size());

    std::vector<uint32_t> value;
    ASSERT_EQ(lru.Get(0, value), CacheComplex::OK);
    ASSERT_THAT(value, testing::ElementsAre(5ull));
    ASSERT_EQ(lru.Get(1, value), CacheComplex::OK);
    ASSERT_THAT(value, testing::ElementsAre(6ull));

    MockSleep(kSleep);

    ASSERT_EQ(lru.Get(0, value), CacheComplex::EXPIRED);
    ASSERT_EQ(lru.Get(1, value), CacheComplex::EXPIRED);

    ASSERT_EQ(lru.Get(2, value), CacheComplex::NOT_FOUND);
    lru.Insert(2, {7ull});
    ASSERT_EQ(lru.Get(2, value), CacheComplex::OK);
    ASSERT_THAT(value, testing::ElementsAre(7ull));
  }

  {
    CacheComplex lru;
    lru.SetMaxSize(2ul);
    lru.SetExpiration(std::chrono::milliseconds(100));
    MockNowSet(kStartTP);

    lru.Insert(0, {5ull});
    lru.Insert(1, {6ull});

    ASSERT_EQ(2ul, lru.Size());

    std::vector<uint32_t> value;
    ASSERT_EQ(lru.Get(0, value), CacheComplex::OK);
    ASSERT_THAT(value, testing::ElementsAre(5ull));
    ASSERT_EQ(lru.Get(1, value), CacheComplex::OK);
    ASSERT_THAT(value, testing::ElementsAre(6ull));

    MockSleep(kSleep);

    ASSERT_EQ(lru.Get(0, value), CacheComplex::EXPIRED);
    ASSERT_EQ(lru.Get(1, value), CacheComplex::EXPIRED);

    ASSERT_EQ(lru.Get(2, value), CacheComplex::NOT_FOUND);
    lru.Insert(2, {7ull});
    ASSERT_EQ(lru.Get(2, value), CacheComplex::OK);
    ASSERT_THAT(value, testing::ElementsAre(7ull));
  }

  {
    CacheComplexKeyValue lru(equal);
    lru.SetMaxSize(2ul);
    lru.SetExpiration(std::chrono::milliseconds(100));
    MockNowSet(kStartTP);

    const ComplexKey k0{0, "0"};
    const ComplexKey k1{1, "1"};
    lru.Insert(k0, {5ull});
    lru.Insert(k1, {6ull});

    ASSERT_EQ(2ul, lru.Size());

    std::vector<uint32_t> value;
    ASSERT_EQ(lru.Get(k0, value), CacheComplexKeyValue::OK);
    ASSERT_THAT(value, testing::ElementsAre(5ull));
    ASSERT_EQ(lru.Get(k1, value), CacheComplexKeyValue::OK);
    ASSERT_THAT(value, testing::ElementsAre(6ull));

    MockSleep(kSleep);

    ASSERT_EQ(lru.Get(k0, value), CacheComplexKeyValue::EXPIRED);
    ASSERT_EQ(lru.Get(k1, value), CacheComplexKeyValue::EXPIRED);

    const ComplexKey k2{2, "2"};
    ASSERT_EQ(lru.Get(k2, value), CacheComplexKeyValue::NOT_FOUND);
    lru.Insert(k2, {7ull});
    ASSERT_EQ(lru.Get(k2, value), CacheComplexKeyValue::OK);
    ASSERT_THAT(value, testing::ElementsAre(7ull));
  }
}
