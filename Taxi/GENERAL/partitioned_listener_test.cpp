#include <listeners/partitioned_listener.hpp>

#include <array>

#include <userver/storages/redis/mock_subscribe_client.hpp>
#include <userver/utest/utest.hpp>

#include <channels/positions/traits.hpp>

#include <geobus/channels/positions/listener.hpp>
#include <listeners/client_listener_impl.hpp>
#include <test/partitioned_listener_tester.hpp>

namespace {

using PositionsListener = geobus::clients::PositionsListener;
using PartitionedListener =
    geobus::clients::PartitionedListener<PositionsListener>;
using Payload = PartitionedListener::Payload;
using Partitions =
    geobus::subscription::SubscriptionStrategy::PartitionIndexContainer;
using ShardingType = geobus::subscription::SubscriptionStrategy::ShardingType;
using PartitionData = geobus::subscription::SubscriptionStrategy::PartitionData;
using RedisPubSubAutoSubscribe = geobus::clients::RedisPubSubAutoSubscribe;

using Tester = geobus::test::PartitionedListenerTester<PartitionedListener>;

std::shared_ptr<storages::redis::MockSubscribeClient> MakeRedisClient() {
  return std::make_shared<storages::redis::MockSubscribeClient>();
}

void EmptyCallback([[maybe_unused]] const std::string channel,
                   [[maybe_unused]] Payload&& payload) {}

UTEST(TestPartitionedListener, Creation) {
  auto redis_client = MakeRedisClient();
  using testing::_;
  EXPECT_CALL(*redis_client, Subscribe(_, _, _)).Times(0);
  EXPECT_CALL(*redis_client, Psubscribe(_, _, _)).Times(0);
  auto listener =
      PartitionedListener::Create(redis_client, "test-channel", EmptyCallback,
                                  RedisPubSubAutoSubscribe::kNo);
}

struct TestPartitionedListener
    : public ::testing::TestWithParam<PartitionData> {};

UTEST_P(TestPartitionedListener, Simple) {
  const PartitionData& partition_data = GetParam();
  const size_t expected_psubscribe_calls =
      partition_data.partition_index_container.empty() ? 1u : 0u;
  const size_t expected_subscribe_calls =
      partition_data.partition_index_container.size();
  auto redis_client = MakeRedisClient();
  using testing::_;
  EXPECT_CALL(*redis_client, Subscribe(_, _, _))
      .Times(expected_subscribe_calls)
      .WillRepeatedly([](std::string,
                         storages::redis::SubscriptionToken::OnMessageCb,
                         const ::redis::CommandControl&) {
        return storages::redis::SubscriptionToken{};
      });
  EXPECT_CALL(*redis_client, Psubscribe(_, _, _))
      .Times(expected_psubscribe_calls);

  auto listener =
      PartitionedListener::Create(redis_client, "test-channel", EmptyCallback,
                                  RedisPubSubAutoSubscribe::kNo);
  Tester::ResubscribeTo(*listener, partition_data);
}

auto MakeTestData() {
  return std::array{
      // clang-format off
    PartitionData{ShardingType::NoSharding, Partitions{}},
    PartitionData{ShardingType::Sharding, Partitions{0u}},
    PartitionData{ShardingType::Sharding, Partitions{1u}},
    PartitionData{ShardingType::Sharding, Partitions{0u, 2u}},
    PartitionData{ShardingType::Sharding, Partitions{1u, 3u}},
    PartitionData{ShardingType::Sharding, Partitions{0u, 2u, 4u}},
    PartitionData{ShardingType::Sharding, Partitions{1u, 3u, 5u}},
    PartitionData{ShardingType::Sharding, Partitions{0u, 3u}},
    PartitionData{ShardingType::Sharding, Partitions{1u, 4u}},
    PartitionData{ShardingType::Sharding, Partitions{2u, 5u}},
    PartitionData{ShardingType::Sharding, Partitions{0u, 10u, 100u}}
      // clang-format on
  };
}

INSTANTIATE_UTEST_SUITE_P(TestPartitionedListener, TestPartitionedListener,
                          ::testing::ValuesIn(MakeTestData()));

}  // namespace
