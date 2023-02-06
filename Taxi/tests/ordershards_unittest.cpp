#include <gtest/gtest.h>

#include <unordered_map>

#include <userver/utest/utest.hpp>

#include <util/order_shard_gen.hpp>

TEST(GenShardByWeightedConfig, Correctness) {
  std::vector<order_core::util::Shard> shards = {
      {/* weight */ 0, /* id */ 0},
      {/* weight */ 3, /* id */ 1},
      {/* weight */ 1, /* id */ 2},
      {/* weight */ 10, /* id */ 3},
  };

  std::mt19937 rng(42);
  std::unordered_map<uint64_t, uint64_t> cnt;
  for (int i = 0; i < 1000; ++i) {
    ++cnt[order_core::util::GenShardByWeightedConfig(rng, shards)];
  }
  ASSERT_EQ(cnt.size(), 3);
  ASSERT_GE(cnt[1], 206);
  ASSERT_GE(cnt[2], 58);
  ASSERT_GE(cnt[3], 636);
}
