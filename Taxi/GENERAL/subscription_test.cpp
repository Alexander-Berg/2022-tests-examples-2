
#include <array>

#include <userver/utest/utest.hpp>

#include <geobus/subscription/config.hpp>
#include <geobus/subscription/config_change_notifier.hpp>
#include <geobus/subscription/fixed_sharding_equal_subscription.hpp>
#include <geobus/subscription/strategy_change_receiver.hpp>

namespace {

using Config = geobus::subscription::Config;
using NoShardingConfig = geobus::subscription::NoShardingConfig;
using HashingShardingConfig = geobus::subscription::HashingShardingConfig;
using ConfigChangeNotifier = geobus::subscription::ConfigChangeNotifier;
using SubscriptionStrategy = geobus::subscription::SubscriptionStrategy;
using ShardingType = SubscriptionStrategy::ShardingType;
using PartitionData = SubscriptionStrategy::PartitionData;
using FixedShardingEqualSubscription =
    geobus::subscription::FixedShardingEqualSubscription;
using StrategyChangeReceiver = geobus::subscription::StrategyChangeReceiver;
using StrategyChangeNotifier = geobus::subscription::StrategyChangeNotifier;
using StrategyChangeSubscription = StrategyChangeNotifier::Subscription;

auto GenerateGarbage() {
  return PartitionData{ShardingType::Sharding, {255u, 255u, 255u, 255u}};
}

class TestReceiver : public StrategyChangeReceiver {
 public:
  TestReceiver() : partition_data_{GenerateGarbage()} {}
  ~TestReceiver() { subscription_.Unsubscribe(); }
  void Subscribe(StrategyChangeNotifier& notifier) {
    subscription_ = notifier.RegisterReceiver(this);
  }

  const auto& GetPartitionsForSubscribe() const { return partition_data_; }

  void OnChange(const SubscriptionStrategy& strategy) override {
    partition_data_ = strategy.GetPartitionsForSubscribe();
  }

 private:
  PartitionData partition_data_;
  StrategyChangeSubscription subscription_;
};

struct TestParam {
  Config new_config;
  size_t shards_count;
  size_t shard_index;
  size_t max_partitions_count;
  PartitionData expected;
};

struct SubscriptionTest : public ::testing::TestWithParam<TestParam> {};

auto MakeTestData() {
  return std::array{
      // clang-format off
      TestParam{NoShardingConfig{}, 1u, 0u, 0u, {ShardingType::NoSharding, {}}},
      TestParam{HashingShardingConfig{2}, 1u, 0u, 0u, {ShardingType::Sharding, {0u, 1u}}},
      TestParam{HashingShardingConfig{3}, 1u, 0u, 0u, {ShardingType::Sharding, {0u, 1u, 2u}}},

      TestParam{NoShardingConfig{}, 2u, 0u, 0u, {ShardingType::NoSharding, {}}},
      TestParam{NoShardingConfig{}, 2u, 1u, 0u, {ShardingType::NoSharding, {}}},

      TestParam{HashingShardingConfig{2}, 2u, 0u, 0u, {ShardingType::Sharding, {0u}}},
      TestParam{HashingShardingConfig{2}, 2u, 1u, 0u, {ShardingType::Sharding, {1u}}},

      TestParam{HashingShardingConfig{6}, 2u, 0u, 0u, {ShardingType::Sharding, {0u, 2u, 4u}}},
      TestParam{HashingShardingConfig{6}, 2u, 1u, 0u, {ShardingType::Sharding, {1u, 3u, 5u}}},

      TestParam{HashingShardingConfig{6}, 3u, 0u, 0u, {ShardingType::Sharding, {0u, 3u}}},
      TestParam{HashingShardingConfig{6}, 3u, 1u, 0u, {ShardingType::Sharding, {1u, 4u}}},
      TestParam{HashingShardingConfig{6}, 3u, 2u, 0u, {ShardingType::Sharding, {2u, 5u}}},

      TestParam{HashingShardingConfig{2}, 3u, 0u, 0u, {ShardingType::Sharding, {0u}}},
      TestParam{HashingShardingConfig{2}, 3u, 1u, 0u, {ShardingType::Sharding, {1u}}},
      TestParam{HashingShardingConfig{2}, 3u, 2u, 0u, {ShardingType::Sharding, {}}},

      // Check max_partition_count
      TestParam{HashingShardingConfig{6}, 1u, 0u, 2u, {ShardingType::Sharding, {0u, 1u}}}
      // clang-format on
  };
}

UTEST_P(SubscriptionTest, Simple) {
  ConfigChangeNotifier source;
  auto strategy = std::make_shared<FixedShardingEqualSubscription>(
      NoShardingConfig{}, GetParam().shards_count, GetParam().shard_index,
      GetParam().max_partitions_count);
  strategy->Subscribe(source);
  auto target = std::make_shared<TestReceiver>();
  target->Subscribe(*strategy);

  // Send new config through chain. Final receiver state should changed
  source.SendChange(GetParam().new_config);
  auto actual = target->GetPartitionsForSubscribe();
  auto expected = GetParam().expected;
  ASSERT_EQ(actual.sharding_type, expected.sharding_type);
  ASSERT_EQ(actual.partition_index_container,
            expected.partition_index_container);
}

INSTANTIATE_UTEST_SUITE_P(SubscriptionTest, SubscriptionTest,
                          ::testing::ValuesIn(MakeTestData()));

}  // namespace
