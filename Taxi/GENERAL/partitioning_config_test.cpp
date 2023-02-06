#include <userver/utest/utest.hpp>

#include <geobus/subscription/partitioning_config.hpp>

namespace {

using PartitioningConfig = geobus::subscription::PartitioningConfig;
using Configs = geobus::subscription::impl::Configs;
using Config = geobus::subscription::Config;
using NoShardingConfig = geobus::subscription::NoShardingConfig;
using HashingShardingConfig = geobus::subscription::HashingShardingConfig;
using Address = geobus::channels::Address;
using RedisName = geobus::channels::RedisName;
using ChannelName = geobus::channels::ChannelName;

const std::string kRedisNameStr{"some-redis"};
const RedisName kRedisName{kRedisNameStr};

auto MakeAddress(std::string channel_name) {
  return Address{kRedisName, ChannelName{std::move(channel_name)}};
}

const auto kNoPartitionedAddress = MakeAddress("no-partition-channel");
const auto kPartitionedAddress = MakeAddress("partitioned-channel");
const auto kAbsentAddress = MakeAddress("absent-in-config-channel");

auto MakeConfigs() {
  Configs result;
  result[kNoPartitionedAddress] = NoShardingConfig{};
  result[kPartitionedAddress] = HashingShardingConfig{2ull};
  return result;
}

TEST(ChannelsConfigTest, DefaultConstructed) {
  const PartitioningConfig config(Configs{});
  const Address address{RedisName("some_redis_name"),
                        ChannelName("some:channel:name")};

  // Default-constructed PartitioningConfig does not contain any Configs. So it
  // must return default, which is 'partitioning disabled'
  const Config expected{NoShardingConfig{}};
  ASSERT_EQ(expected, config.GetFor(address));
}

TEST(ChannelsConfigTest, Simple) {
  const PartitioningConfig config(MakeConfigs());

  ASSERT_TRUE(std::holds_alternative<NoShardingConfig>(
      config.GetFor(kNoPartitionedAddress)));

  ASSERT_TRUE(std::holds_alternative<HashingShardingConfig>(
      config.GetFor(kPartitionedAddress)));

  ASSERT_TRUE(
      std::holds_alternative<NoShardingConfig>(config.GetFor(kAbsentAddress)));
}

}  // namespace
