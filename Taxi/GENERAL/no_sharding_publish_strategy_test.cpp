#include "no_sharding_publish_strategy.hpp"

#include <userver/utest/utest.hpp>

namespace {

using geobus::sharding::DriverId;
using geobus::sharding::NoShardingPublishStrategy;
using geobus::sharding::Position;
using geobus::sharding::Shards;

TEST(NoShardingPublishStrategy, ShardsCount) {
  NoShardingPublishStrategy strategy;
  ASSERT_EQ(1, strategy.GetShardsCount());
}

TEST(NoShardingPublishStrategy, ShardsForDriver) {
  NoShardingPublishStrategy strategy;
  const auto shards = Shards::OnlyOne(0);
  ASSERT_EQ(shards, strategy.GetShardsForDriver(DriverId{}, Position{}));
}

TEST(NoShardingPublishStrategy, ShardName) {
  NoShardingPublishStrategy strategy;
  const std::string channel_base_name{"some:channel"};
  ASSERT_EQ(channel_base_name, strategy.GetShardName(channel_base_name, 0));
}

}  // namespace
