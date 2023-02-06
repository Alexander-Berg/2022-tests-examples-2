#include <publishers/publish_strategies.hpp>

#include <array>
#include <functional>

#include <userver/utest/utest.hpp>

#include <geobus/channels_meta/channels_addresses.hpp>
#include <sharding/hashing_sharding_publish_strategy.hpp>
#include <sharding/no_sharding_publish_strategy.hpp>

namespace {

using AddressId = geobus::channels::AddressId;
using RedisName = geobus::channels::RedisName;
using ChannelName = geobus::channels::ChannelName;

using NoShardingConfig = geobus::subscription::NoShardingConfig;
using HashingShardingConfig = geobus::subscription::HashingShardingConfig;
using ConfigsImpl = geobus::subscription::impl::Configs;
using PartitioningConfig = geobus::subscription::PartitioningConfig;

using Address = geobus::channels::Address;
using RawAddresses = geobus::channels::impl::RawAddresses;
using ChannelsAddresses = geobus::channels::ChannelsAddresses;

using NoShardingPublishStrategy = geobus::sharding::NoShardingPublishStrategy;
using HashingShardingPublishStrategy =
    geobus::sharding::HashingShardingPublishStrategy;

using PublishStrategies = geobus::publishers::PublishStrategies;
using Keeper = geobus::sharding::PublishStrategyKeeper;

using KeeperPredicate = std::function<bool(const Keeper&)>;

bool IsNoShardingStrategy(const Keeper& keeper) {
  auto strategy = keeper.Get();
  return dynamic_cast<const NoShardingPublishStrategy*>(&**strategy) != nullptr;
}

auto MakeIsHashingPredicate(int shards_count) {
  return [shards_count](const Keeper& keeper) {
    auto strategy = keeper.Get();
    auto hashing_strategy =
        dynamic_cast<const HashingShardingPublishStrategy*>(&**strategy);
    return hashing_strategy != nullptr &&
           hashing_strategy->GetShardsCount() == shards_count;
  };
}

const AddressId kInterestingAddressId{"some-address-id"};
const Address kInterestingAddress{RedisName{"some-redis"},
                                  ChannelName{"some-channel"}};

auto MakeChannelsAddresses() {
  RawAddresses raw_addresses{{kInterestingAddressId, kInterestingAddress}};
  return std::make_shared<const ChannelsAddresses>(std::move(raw_addresses));
}

auto MakeEmptyConfig() { return PartitioningConfig{{}}; }

auto MakeConfigWithInterestingChannel() {
  ConfigsImpl configs{{kInterestingAddress, HashingShardingConfig{2}}};
  return PartitioningConfig{std::move(configs)};
}

struct TestParam {
  PartitioningConfig initial_config;
  PartitioningConfig new_config;
  KeeperPredicate check_initial;
  KeeperPredicate check_after_config_change;
};

auto MakeTestData() {
  return std::array{
      // clang-format off
        TestParam{
            MakeEmptyConfig(),
            MakeEmptyConfig(),
            IsNoShardingStrategy,
            IsNoShardingStrategy
        },
        TestParam{
            MakeEmptyConfig(),
            MakeConfigWithInterestingChannel(),
            IsNoShardingStrategy,
            MakeIsHashingPredicate(2)
        },
        TestParam{
            MakeConfigWithInterestingChannel(),
            MakeEmptyConfig(),
            MakeIsHashingPredicate(2),
            IsNoShardingStrategy
        }
      // clang-format on
  };
}

struct PublishStrategiesTest : ::testing::TestWithParam<TestParam> {};

UTEST_P(PublishStrategiesTest, Simple) {
  PublishStrategies strategies{MakeChannelsAddresses(),
                               GetParam().initial_config};
  auto keeper = strategies.GetFor(kInterestingAddressId);
  ASSERT_PRED1(GetParam().check_initial, *keeper);

  strategies.SetConfig(GetParam().new_config);
  ASSERT_PRED1(GetParam().check_after_config_change, *keeper);
}

INSTANTIATE_UTEST_SUITE_P(PublishStrategiesTest, PublishStrategiesTest,
                          ::testing::ValuesIn(MakeTestData()));

}  // namespace
