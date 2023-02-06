#include <vector>

#include <gtest/gtest.h>

#include <caches/buckets/cache.hpp>

namespace {

using Data = std::vector<std::string>;
using Bucket = caches::buckets::Bucket<Data>;
using Gen = caches::buckets::Generation;
using Cache = caches::buckets::Cache<4, Data>;

const std::string kValue{"value"};

const Data kEmpty{};
const Data kTest1{"32u", "52u", "128u"};
const Data kTest2{"104u", "38u", "34u"};

}  // namespace

TEST(Buckets, Generation) {
  const Bucket bucket{Gen{10u}};
  ASSERT_EQ(bucket.GetGeneration(), Gen{10u});

  const Bucket next_gen{*bucket, Gen{11u}};
  ASSERT_EQ(next_gen.GetGeneration(), Gen{11u});
}

TEST(Buckets, GenerationLimit) {
  const Bucket bucket{caches::buckets::MaxGeneration()};
  ASSERT_EQ(bucket.GetGeneration(), caches::buckets::MaxGeneration());

  const Bucket next_gen{*bucket, bucket.GetGeneration() + 1u};
  ASSERT_EQ(next_gen.GetGeneration(), Gen{0u});
}
