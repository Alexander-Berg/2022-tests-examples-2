#include "hashing_sharding_publish_strategy.hpp"

#include <userver/utils/enumerate.hpp>

#include <userver/utest/utest.hpp>

namespace {

using geobus::sharding::DriverId;
using geobus::sharding::HashingShardingPublishStrategy;
using geobus::sharding::Position;
using geobus::sharding::Shards;

inline bool OnlyOne(const Shards& shards) { return shards.size() == 1; }

TEST(HashingShardingPublishStrategy, ShardsCount) {
  HashingShardingPublishStrategy strategy{12};
  ASSERT_EQ(12, strategy.GetShardsCount());
}

TEST(HashingShardingPublishStrategy, ShardsForDriver) {
  HashingShardingPublishStrategy strategy{12};
  ASSERT_TRUE(OnlyOne(strategy.GetShardsForDriver(DriverId{}, Position{})));
}

TEST(HashingShardingPublishStrategy, ShardName) {
  const int shards_count = 12;
  HashingShardingPublishStrategy strategy{shards_count};
  const std::string channel_base_name{"some:channel"};
  const std::vector<std::string> channel_names = [&] {
    std::vector<std::string> result;
    result.reserve(shards_count);
    const auto delimeter = '@';
    for (int i = 0; i < shards_count; ++i) {
      result.push_back(channel_base_name + delimeter + std::to_string(i));
    }
    return result;
  }();
  for (auto&& [shard, shard_name] : ::utils::enumerate(channel_names)) {
    ASSERT_EQ(shard_name, strategy.GetShardName(channel_base_name, shard));
  }
}

}  // namespace
