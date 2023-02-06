#include "aggregating_publisher.hpp"

#include <algorithm>
#include <array>
#include <vector>

#include <userver/engine/single_consumer_event.hpp>
#include <userver/utest/utest.hpp>

#include <userver/storages/redis/mock_client_google.hpp>

#include <channels/positions/traits.hpp>
#include <geobus/channels/positions/track_point.hpp>
#include <geobus/sharding/channel_name.hpp>
#include <sharding/hashing_sharding_publish_strategy.hpp>
#include <sharding/no_sharding_publish_strategy.hpp>

namespace geobus::clients {

using GMockClient = storages::redis::GMockClient;

using DriverId = geobus::types::DriverId;

using PublishStrategy = geobus::sharding::PublishStrategy;
using NoShardingPublishStrategy = geobus::sharding::NoShardingPublishStrategy;
using HashingShardingPublishStrategy =
    geobus::sharding::HashingShardingPublishStrategy;
using PublishStrategyKeeper = geobus::sharding::PublishStrategyKeeper;

namespace {

auto MakeMockClient() { return std::make_shared<GMockClient>(); }

auto MakeStrategyKeeper(std::unique_ptr<PublishStrategy> strategy) {
  return std::make_shared<PublishStrategyKeeper>(std::move(strategy));
}
auto MakeNoShardingStrategy() {
  return MakeStrategyKeeper(std::make_unique<NoShardingPublishStrategy>());
}
auto MakeHashingShardingStrategy(size_t shards_count) {
  return MakeStrategyKeeper(
      std::make_unique<HashingShardingPublishStrategy>(shards_count));
}

struct WaitForCount {
  WaitForCount(size_t count, engine::SingleConsumerEvent* event)
      : required_count(count), processed(event) {}

  WaitForCount() = default;

  void CountReached(size_t x) {
    if (required_count == x) {
      processed->Send();
    }
  }

  template <typename T>
  void BufferPreSend(const T&) noexcept {}

  size_t required_count = 0;
  engine::SingleConsumerEvent* processed = nullptr;
};

struct WaitForSend {
  WaitForSend(engine::SingleConsumerEvent* event) : processed(event) {}

  WaitForSend() = default;

  void CountReached(size_t) noexcept {}

  void BufferPreSend(const std::vector<types::DriverPosition>&) {
    processed->Send();
  }

  engine::SingleConsumerEvent* processed = nullptr;
};

}  // namespace

UTEST(AggregatingPublisher, NoSharding) {
  using AggregatingPublisher =
      geobus::clients::AggregatingPublisher<types::DriverPosition,
                                            WaitForCount>;
  using RawPublisher = geobus::clients::RawPublisher<types::DriverPosition>;

  using ::testing::_;

  generators::PositionsGenerator positions_generator;
  auto strategy_keeper = MakeNoShardingStrategy();
  auto redis_mock = MakeMockClient();
  auto channel_name = std::string{"test-channel"};
  EXPECT_CALL(*redis_mock, Publish(channel_name, _, _, _)).Times(2);

  size_t positions_count = 200;
  size_t max_message_size = 100;

  std::shared_ptr<RawPublisher> raw_publisher(
      std::make_shared<RawPublisher>(redis_mock));
  engine::SingleConsumerEvent all_processed;
  WaitForCount waiter{positions_count, &all_processed};

  AggregatingPublisherParams params;
  params.channel_name = channel_name;
  params.max_publish_delay = std::chrono::hours{100};
  params.max_message_size = max_message_size;
  params.strategy_keeper = strategy_keeper;
  AggregatingPublisher publisher(params, raw_publisher);

  publisher.SetDebugCallbacks(waiter);
  publisher.EnablePublishing(true);

  for (size_t i = 0; i < positions_count; ++i) {
    auto elem = positions_generator.CreateElement(i);
    ASSERT_TRUE(elem.IsValid());
    publisher.Publish(std::move(elem));
  }

  // Start only after data was put into MPSCQueue.
  publisher.Start();

  EXPECT_TRUE(all_processed.WaitForEventFor(std::chrono::milliseconds{500}))
      << publisher.GetDebugStats().published;
}

UTEST(AggregatingPublisher, EqualSharding) {
  using AggregatingPublisher =
      geobus::clients::AggregatingPublisher<types::DriverPosition,
                                            WaitForCount>;
  using RawPublisher = geobus::clients::RawPublisher<types::DriverPosition>;
  using Traits = types::DataTypeTraits<types::DriverPosition>;

  using ::testing::_;

  generators::PositionsGenerator positions_generator;
  auto strategy_keeper = MakeHashingShardingStrategy(2);
  // update strategy
  auto strategy_readable_ptr = strategy_keeper->Get();
  const auto& strategy = **strategy_readable_ptr;
  auto redis_mock = MakeMockClient();
  auto channel_name = std::string{"test-channel"};
  auto shard1_name = geobus::sharding::GetShardName(channel_name, 0);
  auto shard2_name = geobus::sharding::GetShardName(channel_name, 1);
  EXPECT_CALL(*redis_mock, Publish(shard1_name, _, _, _)).Times(1);
  EXPECT_CALL(*redis_mock, Publish(shard2_name, _, _, _)).Times(1);

  size_t positions_count = 100;

  // Generate 100 positions for every shard
  std::vector<std::vector<types::DriverPosition>> per_shard_positions;
  per_shard_positions.resize(2);  // we have only 2 shards

  size_t counter = 0;
  while (per_shard_positions[0].size() < positions_count ||
         per_shard_positions[1].size() < positions_count) {
    auto elem = positions_generator.CreateElement(counter++);
    ASSERT_TRUE(elem.IsValid());
    const auto partitions_for_driver = strategy.GetShardsForDriver(
        Traits::GetDriverId(elem), Traits::GetDriverPosition(elem));
    // Only one partition per driver please
    ASSERT_EQ(1, partitions_for_driver.size());

    const size_t partition = partitions_for_driver[0];

    if (per_shard_positions[partition].size() < positions_count) {
      per_shard_positions[partition].push_back(elem);
    }
  }

  ASSERT_EQ(positions_count, per_shard_positions[0].size());
  ASSERT_EQ(positions_count, per_shard_positions[1].size());

  size_t max_message_size = 100;

  std::shared_ptr<RawPublisher> raw_publisher(
      std::make_shared<RawPublisher>(redis_mock));
  engine::SingleConsumerEvent all_processed;
  WaitForCount waiter{positions_count, &all_processed};

  AggregatingPublisherParams params;
  params.channel_name = channel_name;
  params.max_publish_delay = std::chrono::hours{100};
  params.max_message_size = max_message_size;
  params.strategy_keeper = strategy_keeper;
  AggregatingPublisher publisher(params, raw_publisher);

  publisher.SetDebugCallbacks(waiter);
  publisher.EnablePublishing(true);

  for (size_t i = 0; i < positions_count; ++i) {
    publisher.Publish(std::move(per_shard_positions[0][i]));
    publisher.Publish(std::move(per_shard_positions[1][i]));
  }

  // Start only after data was put into MPSCQueue.
  publisher.Start();

  EXPECT_TRUE(all_processed.WaitForEventFor(std::chrono::milliseconds{500}))
      << publisher.GetDebugStats().published;
}

TEST(AggregatingPublisher, MaxPublishDelay) {
  using AggregatingPublisher =
      geobus::clients::AggregatingPublisher<types::DriverPosition, WaitForSend>;
  using RawPublisher = geobus::clients::RawPublisher<types::DriverPosition>;

  using ::testing::_;
  RunInCoro(
      [] {
        generators::PositionsGenerator positions_generator;
        auto strategy_keeper = MakeNoShardingStrategy();
        auto redis_mock = MakeMockClient();
        auto channel_name = std::string{"test-channel"};
        EXPECT_CALL(*redis_mock, Publish(channel_name, _, _, _)).Times(1);

        // Here, we test that sending one(1) position will trigger sending
        // a whole message with this position after max_publish_delay time.
        // Because max_message_size is 100, publishing one is not enougth to
        // fill a buffer (and trigger sending a buffer). So, second mechanism
        // should work, one that checks that position should not be delayed more
        // then by max_publish_delay milliseconds

        size_t max_message_size = 100;

        std::shared_ptr<RawPublisher> raw_publisher(
            std::make_shared<RawPublisher>(redis_mock));
        engine::SingleConsumerEvent pos_send;
        WaitForSend waiter{&pos_send};

        AggregatingPublisherParams params;
        params.channel_name = channel_name;
        params.max_publish_delay = std::chrono::milliseconds{10};
        params.max_message_size = max_message_size;
        params.strategy_keeper = strategy_keeper;
        AggregatingPublisher publisher(params, raw_publisher);

        publisher.SetDebugCallbacks(waiter);
        publisher.EnablePublishing(true);

        // Send one position
        auto elem = positions_generator.CreateElement(1);
        ASSERT_TRUE(elem.IsValid());
        publisher.Publish(std::move(elem));

        // Start only after data was put into MPSCQueue.
        publisher.Start();

        EXPECT_TRUE(pos_send.WaitForEventFor(std::chrono::milliseconds{500}))
            << publisher.GetDebugStats().published;
      },
      3);
}

}  // namespace geobus::clients
