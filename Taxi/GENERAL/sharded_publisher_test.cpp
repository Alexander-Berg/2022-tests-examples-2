#include "sharded_publisher.hpp"

#include <algorithm>
#include <array>
#include <vector>

#include <userver/utest/utest.hpp>

#include <userver/storages/redis/mock_client_google.hpp>

#include <channels/positions/lowlevel.hpp>
#include <geobus/channels/positions/track_point.hpp>
#include <geobus/sharding/channel_name.hpp>
#include <sharding/data_type_traits_for_position_event.hpp>
#include <sharding/hashing_sharding_publish_strategy.hpp>
#include <sharding/no_sharding_publish_strategy.hpp>
#include <sharding/sharded_publisher_impl.hpp>
#include <test/lowlevel_comparisons.hpp>

namespace {

using GMockClient = storages::redis::GMockClient;

using DriverId = geobus::types::DriverId;
using TrackPoint = geobus::lowlevel::TrackPoint;
using PositionEvent = geobus::lowlevel::PositionEvent;

using ShardedPublisher = geobus::sharding::ShardedPublisher<PositionEvent>;
using Payload = ShardedPublisher::Payload;
using ShardedPayload = geobus::sharding::impl::ShardedPayload<PositionEvent>;
using PublishStrategy = geobus::sharding::PublishStrategy;
using NoShardingPublishStrategy = geobus::sharding::NoShardingPublishStrategy;
using HashingShardingPublishStrategy =
    geobus::sharding::HashingShardingPublishStrategy;
using PublishStrategyKeeper = geobus::sharding::PublishStrategyKeeper;

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

auto MakeShardNames(const std::string& channel_base_name, size_t shards_count) {
  std::vector<std::string> result;
  result.reserve(shards_count);
  for (size_t i = 0; i < shards_count; ++i) {
    result.emplace_back(geobus::sharding::GetShardName(channel_base_name, i));
  }
  return result;
}

auto EmptyPayload() { return Payload{}; }
auto MakeDriverId(int number) {
  return DriverId{"dbid_uuid" + std::to_string(number)};
}
auto MakeTrackPoint(int number) {
  const double origin = 55.735153;
  const double step = 0.000139;
  return TrackPoint(origin + number * step,  // longitude
                    origin - number * step,  // latitude
                    36.0,                    // azimuth
                    60.0,                    // speed
                    {},                      // timestamp
                    geobus::types::PositionSource::Gps);
}
auto MakePosition(int number) {
  return geobus::lowlevel::DriverPositionInfo{MakeDriverId(number),
                                              MakeTrackPoint(number)};
}
auto FullPayload() {
  Payload result{
      {
          // positions
          // clang-format off
          MakePosition(0),
          MakePosition(1),
          MakePosition(2),
          MakePosition(3)
          // clang-format on
      },
      {}  // time_orig, in test we don't care
  };
  return result;
}

struct TestParam {
  // inputs
  std::shared_ptr<PublishStrategyKeeper> strategy_keeper;
  std::string channel_base_name;
  Payload payload;

  // expected outputs
  std::vector<std::string> shard_names;
  ::testing::Cardinality expected_calls;
};

struct TestShardedPublisher : public ::testing::TestWithParam<TestParam> {};

auto MakeTestData() {
  using ::testing::Between;
  using ::testing::Exactly;
  const std::string channel_name{"channel_name"};
  const size_t shards_count = 2;
  const auto& shard_names = MakeShardNames(channel_name, shards_count);

  return std::vector<TestParam>{
      // clang-format off
      {
          MakeNoShardingStrategy(),
          channel_name,
          EmptyPayload(),
          {channel_name},
          Exactly(0)
      },
      {
          MakeNoShardingStrategy(),
          channel_name,
          FullPayload(),
          {channel_name},
          Exactly(1)
      },
      {
          MakeHashingShardingStrategy(shards_count),
          channel_name,
          EmptyPayload(),
          shard_names,
          Exactly(0)
      },
      {
          MakeHashingShardingStrategy(shards_count),
          channel_name,
          FullPayload(),
          shard_names,
          Between(1, 2)
      }
      // clang-format on
  };
}

UTEST_P(TestShardedPublisher, BaseSharding) {
  const auto& param = GetParam();

  auto redis_mock = MakeMockClient();
  using testing::_;
  using testing::AnyOfArray;
  EXPECT_CALL(*redis_mock, Publish(AnyOfArray(param.shard_names), _, _, _))
      .Times(param.expected_calls);

  ShardedPublisher sharded_publisher{param.strategy_keeper};
  ShardedPublisher::Publisher lowlevel_publisher{
      "redis_name", param.channel_base_name, redis_mock};

  sharded_publisher.Publish(lowlevel_publisher, param.channel_base_name,
                            param.payload);
}

INSTANTIATE_UTEST_SUITE_P(TestShardedPublisher, TestShardedPublisher,
                          ::testing::ValuesIn(MakeTestData()));

auto MakePayload(size_t size) {
  Payload result{{}, {}};
  result.positions.reserve(size);
  for (size_t i = 0; i < size; ++i) {
    result.positions.emplace_back(MakePosition(i));
  }
  return result;
}

auto Split(const Payload& payload, int shards_count) {
  const HashingShardingPublishStrategy strategy{shards_count};
  return geobus::sharding::impl::SplitByShards<PositionEvent>(payload,
                                                              strategy);
}

auto Merge(const ShardedPayload& sharded_payload) {
  Payload result;
  for (const auto& shard : sharded_payload) {
    result.positions.insert(result.positions.end(), shard.positions.begin(),
                            shard.positions.end());
    result.time_orig = shard.time_orig;
  }
  return result;
}

auto Sorted(Payload payload) {
  auto pred = [](const auto& lhs, const auto& rhs) {
    return lhs.driver_id.GetDbidUndscrUuid() <
           rhs.driver_id.GetDbidUndscrUuid();
  };
  std::sort(payload.positions.begin(), payload.positions.end(),
            std::move(pred));
  return payload;
}

bool EqualTimes(const ShardedPayload& sharded_payload) {
  return std::adjacent_find(sharded_payload.begin(), sharded_payload.end(),
                            [](const auto& lhs, const auto& rhs) {
                              return lhs.time_orig != rhs.time_orig;
                            }) == sharded_payload.end();
}

struct SplitParam {
  SplitParam(size_t payload_size, size_t shards_count)
      : payload_size(payload_size), shards_count(shards_count) {}
  size_t payload_size;
  size_t shards_count;
};

struct SplitTest : public ::testing::TestWithParam<SplitParam> {};

auto MakeTestDataForSplit() {
  std::vector<SplitParam> result;
  const std::array payload_sizes{1u,   2u,   20u,  50u,  100u,
                                 200u, 300u, 400u, 500u, 1000u};
  const std::array shards_counts{1u, 2u, 3u, 6u, 12u, 24u, 72u};

  for (const auto payload_size : payload_sizes) {
    for (const auto shards_count : shards_counts) {
      result.emplace_back(payload_size, shards_count);
    }
  }

  return result;
}

UTEST_P(SplitTest, TestSplit) {
  auto payload = MakePayload(GetParam().payload_size);
  const auto sharded_payload = Split(payload, GetParam().shards_count);

  ASSERT_TRUE(EqualTimes(sharded_payload));

  // sort positions just to use operator==(vector, vector) in assert
  ASSERT_EQ(Sorted(payload), Sorted(Merge(sharded_payload)));
}

INSTANTIATE_UTEST_SUITE_P(SplitTest, SplitTest,
                          ::testing::ValuesIn(MakeTestDataForSplit()));

}  // namespace
